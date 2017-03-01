import click

@click.command()
def Main():
    try:
        import IPython
        IPython.embed()
    except ImportError:
        from code import interact
        interact(local=dict(globals(), **locals()))

