"""Color output utilities"""

from colorama import init, Fore, Style

init(autoreset=True)

def print_logo():
    """Print ZYNOX ASCII logo"""
    logo = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
{Fore.CYAN}║{Fore.YELLOW}   ███████╗██╗   ██╗███╗   ██╗ ██████╗ ██╗  ██╗{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}   ╚══███╔╝╚██╗ ██╔╝████╗  ██║██╔═══██╗╚██╗██╔╝{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}     ███╔╝  ╚████╔╝ ██╔██╗ ██║██║   ██║ ╚███╔╝ {Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}    ███╔╝    ╚██╔╝  ██║╚██╗██║██║   ██║ ██╔██╗ {Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}   ███████╗   ██║   ██║ ╚████║╚██████╔╝██╔╝ ██╗{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝{Fore.CYAN}                ║
{Fore.CYAN}╠═══════════════════════════════════════════════════════════════╣
{Fore.CYAN}║{Fore.GREEN}         AI-Powered File & Folder Creation Tool{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.MAGENTA}      ChatGPT • Gemini • Grok • DeepSeek • Telegram{Fore.CYAN}            ║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(logo)

def green(text): return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
def red(text): return f"{Fore.RED}{text}{Style.RESET_ALL}"
def yellow(text): return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
def cyan(text): return f"{Fore.CYAN}{text}{Style.RESET_ALL}"
def magenta(text): return f"{Fore.MAGENTA}{text}{Style.RESET_ALL}"

def print_about():
    """Print about information"""
    about_text = f"""
{green('ZynoxAI v4.8.15')} - AI-Powered helpful locally executable behavior tools
{magenta('Author:')} Buge Studio | {magenta('License:')} MIT
{magenta('GitHub:')} https://github.com/BugeStudioTeam/Zynox

{magenta('AI Providers:')} GPT, Gemini, Grok, DeepSeek
{magenta('Features:')} Memory, Smart Install, web, Telegram Bot
{magenta('Platforms:')} Termux, Linux, macOS, Windows (WSL)
"""
    print(about_text)