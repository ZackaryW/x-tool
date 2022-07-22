import click

if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from click_shell import shell
from xtool.db import XToolDB
from xtool_ext.shortcuts import XToolShortcuts

@shell(prompt='xtoolCli> ', intro='Welcome to the xtoolCli shell.', invoke_without_command=True)
@click.option(
    '--path', 
    default="./deploy/", 
    help="Path to the deployment folder.", 
    type=click.Path(exists=True, resolve_path=True)
)
@click.option(
    '--source', 
    default="./source/", 
    help="Path to the source folder.", 
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True)
)
@click.pass_context
def cliShell(ctx, path, source):
    db : XToolDB = XToolDB(path, source)
    db._addExtension(XToolShortcuts)

    ctx.obj = db
    ctx.ensure_object(XToolDB)
    
    print("xtool initialized")


@cliShell.command("list")
@click.option("--installed", "-i", is_flag=True, help="List installed packages.")
@click.option("--available", "-a", is_flag=True, help="List available packages.")
@click.option("--complete", "-c", is_flag=True, help="List packages in a complete format.")
@click.pass_context
def cliList(ctx, installed, available, complete):
    db : XToolDB = ctx.obj
    query = {}
    if installed:
        query["isInstalled"] = True
    if available:
        query["isAvailable"] = True

    with db.makeSession() as session:
        pkgs = session.query(db.XToolEntry).filter_by(**query).all()
        for pkg in pkgs:
            if complete:
                print(repr(pkg))
            else:
                print(pkg)

if __name__ == '__main__':
    cliShell()