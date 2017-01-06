
config = {
    # Should we turn on the realtime updater?
    'pdcupdater.enabled': True,

    # Credentials to talk to PDC
    'pdcupdater.pdc': {
        'server': 'https://pdc.fedoraproject.org/rest_api/v1/',
        'insecure': False,  # Enable if using a self-signed cert
        'token': 'AWESOME_SECRET_STRING_GOES_HERE',
        # XXX - getting the token is a bit of a pain, but here's a walk through
        # 1) go to https://pdc.fedoraproject.org/ in your browser and login.
        # 2) go to https://pdc.fedoraproject.org/rest_api/v1/auth/token/obtain/
        # 3) open up the devtools console in your browser, and find the request for the current page.
        # 4) right click to open a context menu and select 'copy as cURL'
        # 5) paste that into a terminal.  It should have your saml cookie.
        # 6) before hitting enter, edit the command to add the following option
        #       -H 'Accept: application/json'   # to tell the API you want data
        # 7) the command should print out your token.
    },

    ## Credentials to talk to FAS
    #'pdcupdater.fas': {
    #    'base_url': 'https://admin.fedoraproject.org/accounts',
    #    'username': 'YOUR_USERNAME_GOES_HERE',
    #    'password': 'AWESOME_SECRET_PASSWORD_GOES_HERE',
    #},

    # PkgDB details
    'pdcupdater.pkgdb_url': 'https://admin.fedoraproject.org/pkgdb',

    # Koji details
    'pdcupdater.koji_url': 'http://koji.fedoraproject.org/kojihub',
    # Use 8 threads to talk to koji in parallel.
    'pdcupdater.koji_io_threads': 8,

    # Where to find composes
    'pdcupdater.old_composes_url': 'https://kojipkgs.fedoraproject.org/compose/',

    # Where to find the fedora-atomic json definitions.
    'pdcupdater.fedora_atomic_git_url': 'https://pagure.io/fedora-atomic/raw/master/f/',

    # We have an explicit list of these in the config so we can turn them on
    # and off individually in production if one is causing an issue.
    'pdcupdater.handlers': [
        'pdcupdater.handlers.persons:NewPersonHandler',
        'pdcupdater.handlers.pkgdb:NewPackageHandler',
        'pdcupdater.handlers.pkgdb:NewPackageBranchHandler',
        'pdcupdater.handlers.rpms:NewRPMHandler',
        'pdcupdater.handlers.compose:NewComposeHandler',

        # https://fedoraproject.org/wiki/User:Ralph/Drafts/Infrastructure/Factory2/ModellingDeps
        'pdcupdater.handlers.depchain.rpms:NewRPMBuildTimeDepChainHandler',
        'pdcupdater.handlers.depchain.rpms:NewRPMRunTimeDepChainHandler',
        'pdcupdater.handlers.depchain.containers:ContainerRPMInclusionDepChainHandler',
    ],

    # Configure tags of interest for various depchain handlers here
    'pdcupdater.ContainerRPMInclusionDepChainHandler.interesting_tags': [
        'f24-docker',
    ],

    # Augment the base fedmsg logging config to also handle pdcupdater loggers.
    'logging': dict(
        loggers=dict(
            pdcupdater={
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console"],
            },
        )
    )
}
