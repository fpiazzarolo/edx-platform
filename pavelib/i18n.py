"""
Internationalization tasks
"""
import sys
import subprocess
from path import Path as path
from paver.easy import task, cmdopts, needs, sh
from .utils.cmd import django_cmd

try:
    from pygments.console import colorize
except ImportError:
    colorize = lambda color, text: text

DEFAULT_SETTINGS = 'devstack'


@task
@needs(
    "pavelib.prereqs.install_prereqs",
    "pavelib.i18n.i18n_validate_gettext",
    "pavelib.assets.compile_coffeescript",
)
@cmdopts([
    ("verbose", "v", "Sets 'verbose' to True"),
])
def i18n_extract(options):
    """
    Extract localizable strings from sources
    """
    verbose = getattr(options, "verbose", None)
    cmd = "i18n_tool extract"

    if verbose:
        cmd += " -vv"

    sh(cmd)


@task
def i18n_fastgenerate():
    """
    Compile localizable strings from sources without re-extracting strings first.
    """
    sh("i18n_tool generate")


@task
@needs("pavelib.i18n.i18n_extract")
def i18n_generate():
    """
    Compile localizable strings from sources, extracting strings first.
    """
    sh("i18n_tool generate")


@task
@needs("pavelib.i18n.i18n_extract")
def i18n_generate_strict():
    """
    Compile localizable strings from sources, extracting strings first.
    Complains if files are missing.
    """
    sh("i18n_tool generate --strict")


@task
@needs("pavelib.i18n.i18n_extract")
def i18n_dummy():
    """
    Simulate international translation by generating dummy strings
    corresponding to source strings.
    """
    sh("i18n_tool dummy")
    # Need to then compile the new dummy strings
    sh("i18n_tool generate")

    # Generate static i18n JS files.
    for system in ['lms', 'cms']:
        sh(django_cmd(system, DEFAULT_SETTINGS, 'compilejsi18n'))


@task
def i18n_validate_gettext():
    """
    Make sure GNU gettext utilities are available
    """

    returncode = subprocess.call(['which', 'xgettext'])

    if returncode != 0:
        msg = colorize(
            'red',
            "Cannot locate GNU gettext utilities, which are "
            "required by django for internationalization.\n (see "
            "https://docs.djangoproject.com/en/dev/topics/i18n/"
            "translation/#message-files)\nTry downloading them from "
            "http://www.gnu.org/software/gettext/ \n"
        )

        sys.stderr.write(msg)
        sys.exit(1)


@task
def i18n_validate_transifex_config():
    """
    Make sure config file with username/password exists
    """
    home = path('~').expanduser()
    config = home / '.transifexrc'

    if not config.isfile or config.getsize == 0:
        msg = colorize(
            'red',
            "Cannot connect to Transifex, config file is missing"
            " or empty: {config} \nSee "
            "http://help.transifex.com/features/client/#transifexrc \n".format(
                config=config,
            )
        )

        sys.stderr.write(msg)
        sys.exit(1)


@task
@needs("pavelib.i18n.i18n_validate_transifex_config")
def i18n_transifex_push():
    """
    Push source strings to Transifex for translation
    """
    sh("i18n_tool transifex push")


@task
@needs("pavelib.i18n.i18n_validate_transifex_config")
def i18n_transifex_pull():
    """
    Pull translated strings from Transifex
    """
    sh("i18n_tool transifex pull")


@task
def i18n_rtl():
    """
    Pull all RTL translations (reviewed AND unreviewed) from Transifex
    """
    sh("i18n_tool transifex rtl")

    print "Now generating langugage files..."

    sh("i18n_tool generate --rtl")

    print "Committing translations..."
    sh('git clean -fdX conf/locale')
    sh('git add conf/locale')
    sh('git commit --amend')


@task
def i18n_ltr():
    """
    Pull all LTR translations (reviewed AND unreviewed) from Transifex
    """
    sh("i18n_tool transifex ltr")

    print "Now generating langugage files..."

    sh("i18n_tool generate --ltr")

    print "Committing translations..."
    sh('git clean -fdX conf/locale')
    sh('git add conf/locale')
    sh('git commit --amend')


@task
@needs(
    "pavelib.i18n.i18n_clean",
    "pavelib.i18n.i18n_transifex_pull",
    "pavelib.i18n.i18n_extract",
    "pavelib.i18n.i18n_dummy",
    "pavelib.i18n.i18n_generate_strict",
)
def i18n_robot_pull():
    """
    Pull source strings, generate po and mo files, and validate
    """

    # sh('paver test_i18n')
    # Tests were removed from repo, but there should still be tests covering the translations
    # TODO: Validate the recently pulled translations, and give a bail option
    sh('git clean -fdX conf/locale/rtl')
    sh('git clean -fdX conf/locale/eo')
    print "\n\nValidating translations with `i18n_tool validate`..."
    sh("i18n_tool validate")

    con = raw_input("Continue with committing these translations (y/n)? ")

    if con.lower() == 'y':
        sh('git add conf/locale')
        sh('git add cms/static/js/i18n')
        sh('git add lms/static/js/i18n')

        sh(
            'git commit --message='
            '"Update translations (autogenerated message)" --edit'
        )


@task
def i18n_clean():
    """
    Clean the i18n directory of artifacts
    """
    sh('git clean -fdX conf/locale')


@task
@needs(
    "pavelib.i18n.i18n_extract",
    "pavelib.i18n.i18n_transifex_push",
)
def i18n_robot_push():
    """
    Extract new strings, and push to transifex
    """
    pass
