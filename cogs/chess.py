import asyncio
import chess
import chess.svg
from config import Config
from discord import Embed, File
from discord.ext import commands
from dotenv import load_dotenv
import os
import secrets
from stockfish import Stockfish
from wand.image import Image
from .utils import reactions


load_dotenv()
CHANNEL = int(os.getenv('CHESS_CHANNEL'))

class ChessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        self.moves = []
        self.total_moves = 0
        self.game_over = False
        self.automatic_moves = False
        self.board = chess.Board()
        self.stockfish = Stockfish()

    def get_board_string(self):
        return f'```{self.board}```'
    
    def save_board_png(self):
        svg = chess.svg.board(self.board, size=350)
        with open('board.svg', 'w') as f:
            f.write(svg)

        with Image(filename='board.svg') as img:
            img.format = 'png'
            img.save(filename='board.png')

    @commands.group(aliases=['c'])
    async def chess(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid **chess** subcommand')

    @chess.command()
    async def new(self, ctx):
        if ctx.channel.id != CHANNEL:
            return

        # TODO archive last game always?
        self.moves = []
        self.total_moves = 0
        self.game_over = False

        self.board = chess.Board()
        self.save_board_png()
        await ctx.send(file=File('board.png'))

    @chess.command()
    async def auto(self, ctx):
        if ctx.channel.id != CHANNEL:
            return
        
        self.automatic_moves = not self.automatic_moves
        await ctx.message.add_reaction(reactions.CHECKMARK_REACTION)

    @chess.command()
    async def board(self, ctx):
        if ctx.channel.id != CHANNEL:
            return

        await ctx.send(file=File('board.png'))

    @chess.command()
    async def undo(self, ctx):
        if ctx.channel.id != CHANNEL:
            return
        
        self.board.pop()
        m = self.moves.pop()
        self.total_moves = self.total_moves - 1

        self.save_board_png()
        await ctx.send(content=f'Deleted previous move `{m}`', file=File('board.png'))

    @chess.command()
    async def history(self, ctx):
        if ctx.channel.id != CHANNEL:
            return
        
        if not self.moves:
            await ctx.message.reply('No moves have been made in the current game.')
            return
        
        await ctx.send(' -> '.join(self.moves))

    @chess.command()
    async def fen(self, ctx):
        if ctx.channel.id != CHANNEL:
            return
        
        await ctx.send(f'```{self.board.fen()}```')

    @chess.command()
    async def info(self, ctx):
        if ctx.channel.id != CHANNEL:
            return
        
        self.stockfish.set_fen_position(self.board.fen())
        best_move = self.stockfish.get_best_move()
        top_moves = self.stockfish.get_top_moves(10)
        legal_moves = ', '.join(str(x) for x in self.board.legal_moves)

        embed = Embed(title=None)
        embed.add_field(name='Best Move', value=best_move)
        embed.add_field(name='Top moves', value=', '.join([x['Move'] for x in top_moves]))
        embed.add_field(name='Legal moves', value=legal_moves)
        await ctx.send(content=None, embed=embed)

    @chess.command()
    async def fools(self, ctx):
        self.board.push_uci('f2f3')
        self.moves.append('f2f3')
        self.total_moves = self.total_moves + 1

        self.board.push_uci('e7e6')
        self.moves.append('e7e6')
        self.total_moves = self.total_moves + 1

        self.board.push_uci('g2g4')
        self.moves.append('g2g4')
        self.total_moves = self.total_moves + 1

        self.board.push_uci('d8h4')
        self.moves.append('d8h4')
        self.total_moves = self.total_moves + 1


        if self.board.is_game_over():
            self.game_over = True
            self.save_board_png()
            m = await ctx.send(content=f'# GAME OVER', file=File('board.png'))
            await m.add_reaction(reactions.CHECKMARK_REACTION)
            return

    async def game_move(self, ctx, move):
        active_player = 'Player' if self.board.turn else 'Computer'

        try:
            self.board.push_uci(move)
        except chess.InvalidMoveError:
            await ctx.message.reply(f'Invalid move. Example: e2e4')
            return
        except chess.IllegalMoveError:
            await ctx.message.reply(f'Illegal move.')
            return
        
        self.stockfish.set_fen_position(self.board.fen())
        self.moves.append(move) # do we need to track moves per player?
        self.total_moves = self.total_moves + 1

        if self.board.is_game_over():
            self.game_over = True
            self.save_board_png()
            m = await ctx.send(content=f'# GAME OVER', file=File('board.png'))
            await m.add_reaction(reactions.CHECKMARK_REACTION)
            return

        self.save_board_png()
        m = await ctx.send(content=f'{active_player} plays `{move}`', file=File('board.png'))

        if self.board.is_check():
            await m.add_reaction(reactions.CHECKMARK_REACTION)

    @chess.command()
    async def best(self, ctx):
        if ctx.channel.id != CHANNEL:
            return
        
        if self.game_over:
            await ctx.send('Current game is over; start a new game.')
            return
        
        move = self.stockfish.get_best_move()
        await self.game_move(ctx, move)

    @chess.command()
    async def go(self, ctx):
        if ctx.channel.id != CHANNEL:
            return
        
        if self.game_over:
            await ctx.send('Current game is over; start a new game.')
            return
        
        top_moves = self.stockfish.get_top_moves(5)
        move = secrets.choice([x['Move'] for x in top_moves])
        await self.game_move(ctx, move)

    @chess.command()
    async def move(self, ctx, move):
        if ctx.channel.id != CHANNEL:
            return
        
        if not move:
            await ctx.message.reply(f'No move specified. Example: move e2e4')
            return
        
        if self.game_over:
            await ctx.send('Current game is over; start a new game.')
            return
        
        # TODO need a better way to handle being able to specify moves for the computer but also respecting turns
        '''
        if not self.board.turn:
            await ctx.message.reply(f'Wait your turn!')
            return
        '''

        move = move.lower()

        await self.game_move(ctx, move)
        await ctx.message.add_reaction(reactions.THUMBS_UP_REACTION)

        # need to make sure this isn't triggered on a game_move() call for player
        if self.automatic_moves:
            await asyncio.sleep(3)
            move = self.stockfish.get_best_move()
            await self.game_move(ctx, move)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(f'error running cmd: {error}')

async def setup(bot):
    await bot.add_cog(ChessCog(bot))
