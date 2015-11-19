
config = {
    'pdcupdater.enabled': True,
    'pdcupdater.pdc': {
        'development-mode': True,  # When this is true, no credentials are used
        'url': 'https://blahblahblah',
        'api_token': 'blahblahblah',
    },

    # We have an explicit list of these in the config so we can turn them on
    # and off individually in production if one is causing an issue.
    'pdcupdater.handlers': [
        'pdcupdater.handlers.pkgdb:NewPackageHandler',
        'pdcupdater.handlers.pkgdb:NewPackageBranchHandler',
        #'pdcupdater.handlers.compose:NewComposeHandler',
        #'pdcupdater.handlers.buildsys:ImageBuildHandler',
        #'pdcupdater.handlers.buildsys:RawhideRPMBuildHandler',
        #'pdcupdater.handlers.bodhi:UpdateRequestCompleteHandler',
        #'pdcupdater.handlers.fas:NewUserHandler',  # This one is cheeseball.
    ],
}
