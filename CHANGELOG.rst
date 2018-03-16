
0.8.3
-----

Fix the test suite.

0.8.2
-----

Commits

- 13edc90be Only retire a package if the dead.package still exists on retiring
  https://github.com/fedora-infra/pdc-updater/commit/13edc90be

0.8.1
-----

Pull Requests

-                   #81, Merge pull request #81 from hanzz/modulemdv2
  https://github.com/fedora-infra/pdc-updater/pull/81

Commits

- 44e0a36dc Use libmodulemd library instead of old deprecated modulemd module.
  https://github.com/fedora-infra/pdc-updater/commit/44e0a36dc
- c5c72bb46 Merge branch 'master' into develop
  https://github.com/fedora-infra/pdc-updater/commit/c5c72bb46
- a19c8c624 0.8.0
  https://github.com/fedora-infra/pdc-updater/commit/a19c8c624

0.8.0
-----

Pull Requests

- Support for libmodulemd, v2.
  https://github.com/fedora-infra/pdc-updater/pull/81

Commits

- d173e6477 0.7.1
  https://github.com/fedora-infra/pdc-updater/commit/d173e6477
- 44e0a36dc Use libmodulemd library instead of old deprecated modulemd module.
  https://github.com/fedora-infra/pdc-updater/commit/44e0a36dc
- c5c72bb46 Merge branch 'master' into develop
  https://github.com/fedora-infra/pdc-updater/commit/c5c72bb46

0.7.1
-----

Include missing vcr-request-data for tests.

0.7.0
-----

Pull Requests

-                   #78, Merge pull request #78 from fedora-infra/fix-tests
  https://github.com/fedora-infra/pdc-updater/pull/78
-                   #79, Merge pull request #79 from fedora-infra/remove-trees
  https://github.com/fedora-infra/pdc-updater/pull/79
-                   #80, Merge pull request #80 from fedora-infra/new-module-api
  https://github.com/fedora-infra/pdc-updater/pull/80

Commits

- 1d6837744 Fix PDC mocks on the latest pdc_client version
  https://github.com/fedora-infra/pdc-updater/commit/1d6837744
- 86678fce3 Remove invalid imports for TestKerberosAuthentication and fix its styling
  https://github.com/fedora-infra/pdc-updater/commit/86678fce3
- 2580832b7 Add Travis CI configuration
  https://github.com/fedora-infra/pdc-updater/commit/2580832b7
- dec9094b2 Remove code for the non-existent "trees" PDC API
  https://github.com/fedora-infra/pdc-updater/commit/dec9094b2
- 1e4c59cb8 Change bulk patch to single patch in unreleasedvariants
  https://github.com/fedora-infra/pdc-updater/commit/1e4c59cb8
- e6ffff4a5 Remove some unused class variables on "ModuleStateChangeHandler"
  https://github.com/fedora-infra/pdc-updater/commit/e6ffff4a5
- 6a848b0c8 Support the new "modules" PDC API
  https://github.com/fedora-infra/pdc-updater/commit/6a848b0c8

0.6.5
-----

Pull Requests

- (@ralphbean)      #75, Add some more logging, to help debug in the future.
  https://github.com/fedora-infra/pdc-updater/pull/75

Commits

- b1ca22f7c Add some more logging, to help debug in the future.
  https://github.com/fedora-infra/pdc-updater/commit/b1ca22f7c
- 634232f82 Change the way we PATCH pdc for modules.
  https://github.com/fedora-infra/pdc-updater/commit/634232f82
- 8b8b001be 0.6.4
  https://github.com/fedora-infra/pdc-updater/commit/8b8b001be
- 3103c3794 Merge branch 'master' into develop
  https://github.com/fedora-infra/pdc-updater/commit/3103c3794

0.6.4
-----

Pull Requests

- (@ralphbean)      #76, Change the way we PATCH pdc for modules.
  https://github.com/fedora-infra/pdc-updater/pull/76

Commits

- a64aaf7ca Change the way we PATCH pdc for modules.
  https://github.com/fedora-infra/pdc-updater/commit/a64aaf7ca

0.6.3
-----

Pull Requests

- (@ralphbean)      #73, Ignore modules in the build state.
  https://github.com/fedora-infra/pdc-updater/pull/73
- (@hanzz)          #74, Use different way to call PDC API to workaround 404 bug for valid modules in PDC.
  https://github.com/fedora-infra/pdc-updater/pull/74

Commits

- 9604e3009 Ignore modules in the build state.
  https://github.com/fedora-infra/pdc-updater/commit/9604e3009
- 66a15a516 Use different way to call PDC API to workaround 404 bug for valid modules in PDC.
  https://github.com/fedora-infra/pdc-updater/commit/66a15a516

0.6.2
-----

Pull Requests

- (@mprahl)         #71, Don't use the environment when constructing a topic for STOMP
  https://github.com/fedora-infra/pdc-updater/pull/71
- (@mprahl)         #72, Support old python-requests-kerberos
  https://github.com/fedora-infra/pdc-updater/pull/72

Commits

- 70193ba8e Don't use the environment when constructing a topic for STOMP
  https://github.com/fedora-infra/pdc-updater/commit/70193ba8e
- ab45b1f2a Remove unneeded force_preemptive flag with Kerberos auth
  https://github.com/fedora-infra/pdc-updater/commit/ab45b1f2a
- 4b1d83166 PEP8 fix
  https://github.com/fedora-infra/pdc-updater/commit/4b1d83166
- 0b2e163ae Add logging when getting a PDC token fails
  https://github.com/fedora-infra/pdc-updater/commit/0b2e163ae

0.6.1
-----

Pull Requests

- (@yashvardhannanavati) #69, Automatic token generation from keytab
  https://github.com/fedora-infra/pdc-updater/pull/69
- (@ralphbean)      #70, Handle case where release[dist_git] contains an explicit None.
  https://github.com/fedora-infra/pdc-updater/pull/70

Commits

- ee572cf30 Handle case where release[dist_git] contains an explicit None.
  https://github.com/fedora-infra/pdc-updater/commit/ee572cf30
- 8a98a3fc4 Automatic token generation from keytab
  https://github.com/fedora-infra/pdc-updater/commit/8a98a3fc4
- 5effdf2be Unit test for auto kerb authentication added
  https://github.com/fedora-infra/pdc-updater/commit/5effdf2be
- aa1d0b313 Add pytest.
  https://github.com/fedora-infra/pdc-updater/commit/aa1d0b313

0.6.0
-----

Pull Requests

- (@ralphbean)      #57, srpm_nevra must not be set when arch is src.
  https://github.com/fedora-infra/pdc-updater/pull/57
- (@ralphbean)      #62, Force creation of parent with type during initialization.
  https://github.com/fedora-infra/pdc-updater/pull/62
- (@ralphbean)      #60, Populate the dist_git_branch value...
  https://github.com/fedora-infra/pdc-updater/pull/60
- (@ralphbean)      #61, Also construct container tags from stable updates tags.
  https://github.com/fedora-infra/pdc-updater/pull/61
- (@mprahl)         #63, Add a handler so that PDC branches are EOL'd when the branch is retired
  https://github.com/fedora-infra/pdc-updater/pull/63
- (@mprahl)         #64, Add some missing doc strings to RetireComponentHandler
  https://github.com/fedora-infra/pdc-updater/pull/64
- (@ralphbean)      #66, Some changes to the retirement handler...
  https://github.com/fedora-infra/pdc-updater/pull/66

Commits

- 6118478b5 srpm_nevra must not be set when arch is src.
  https://github.com/fedora-infra/pdc-updater/commit/6118478b5
- 600b6175e Populate the dist_git_branch value...
  https://github.com/fedora-infra/pdc-updater/commit/600b6175e
- 17edf56ad Also construct container tags from stable updates tags.
  https://github.com/fedora-infra/pdc-updater/commit/17edf56ad
- 7a022d494 Force creation of parent with type during initialization.
  https://github.com/fedora-infra/pdc-updater/commit/7a022d494
- b7341977a Add a handler so that PDC branches are EOL'd when the branch is retired
  https://github.com/fedora-infra/pdc-updater/commit/b7341977a
- 31f7caf33 Break retirement out into its own staticmethod.
  https://github.com/fedora-infra/pdc-updater/commit/31f7caf33
- e2eeec935 Write an init method.
  https://github.com/fedora-infra/pdc-updater/commit/e2eeec935
- e132ab502 Add Docstrings to RetireComponentHandler
  https://github.com/fedora-infra/pdc-updater/commit/e132ab502
- e2d52896c Add the audit function to the RetireComponentHandler handler
  https://github.com/fedora-infra/pdc-updater/commit/e2d52896c
- bcb112faa Add some missing doc strings to RetireComponentHandler
  https://github.com/fedora-infra/pdc-updater/commit/bcb112faa
- 3a2cef32e Make these two work functions re-try-able.
  https://github.com/fedora-infra/pdc-updater/commit/3a2cef32e
- fe8af401d Check pagure instead of cgit.
  https://github.com/fedora-infra/pdc-updater/commit/fe8af401d
- e1b0542b4 Fix those mocks.
  https://github.com/fedora-infra/pdc-updater/commit/e1b0542b4

0.5.9
-----

Pull Requests

-                   #56, Merge pull request #56 from hanzz/module-hash
  https://github.com/fedora-infra/pdc-updater/pull/56

Commits

- d6110bd6a Do not set srpm_nevra to None when adding RPM to PDC
  https://github.com/fedora-infra/pdc-updater/commit/d6110bd6a

0.5.8
-----

Commits

- 694ee3b52 Thank goodness for tests.
  https://github.com/fedora-infra/pdc-updater/commit/694ee3b52

0.5.7
-----

Commits

- fb0e68fa0 Do not die if we cannot find a given tag.  Just warn.
  https://github.com/fedora-infra/pdc-updater/commit/fb0e68fa0
- 61b11a02c Return to dynamically generating list of container tags.
  https://github.com/fedora-infra/pdc-updater/commit/61b11a02c

0.5.6
-----

Pull Requests

-                   #54, Merge pull request #54 from hanzz/module-hash
  https://github.com/fedora-infra/pdc-updater/pull/54

Commits

- ed0707849 Add RPMs built in module to PDC when the module state changes to ready.
  https://github.com/fedora-infra/pdc-updater/commit/ed0707849
- 35bf475b7 Merge branch 'master' into develop
  https://github.com/fedora-infra/pdc-updater/commit/35bf475b7

0.5.5
-----

Pull Requests

-                   #53, Merge pull request #53 from hanzz/module-hash
  https://github.com/fedora-infra/pdc-updater/pull/53

Commits

- b0f14d1f8 Use hash instead of variant_uid for koji_tag, otherwise we hit the 50 characters limit for koji_tag used by Koji.
  https://github.com/fedora-infra/pdc-updater/commit/b0f14d1f8

0.5.4
-----

Commits

- e78b809f8 Provide a default value here.
  https://github.com/fedora-infra/pdc-updater/commit/e78b809f8
- 004117077 Fix tests after #52.
  https://github.com/fedora-infra/pdc-updater/commit/004117077

0.5.3
-----

Pull Requests

- #49, Merge pull request #49 from fedora-infra/feature/fix-fedora-cloud-release
  https://github.com/fedora-infra/pdc-updater/pull/49
- #51, Merge pull request #51 from fedora-infra/feature/spelling-fix
  https://github.com/fedora-infra/pdc-updater/pull/51
- #50, Merge pull request #50 from fedora-infra/old-cruft
  https://github.com/fedora-infra/pdc-updater/pull/50
- #52, Merge pull request #52 from fedora-infra/feature/patch-on-module-done
  https://github.com/fedora-infra/pdc-updater/pull/52

Commits

- e779eba88 Check for NoneType here.
  https://github.com/fedora-infra/pdc-updater/commit/e779eba88
- 93c0deffe Remove new internal field.
  https://github.com/fedora-infra/pdc-updater/commit/93c0deffe
- 8e3174ae1 Remove old cruft.
  https://github.com/fedora-infra/pdc-updater/commit/8e3174ae1
- 6723021ca Fix a spelling mistake.
  https://github.com/fedora-infra/pdc-updater/commit/6723021ca
- 7ffc06a36 Use the variant_uid lookup_field.
  https://github.com/fedora-infra/pdc-updater/commit/7ffc06a36
- 09575def2 Toggle modules to active=True when they are done.
  https://github.com/fedora-infra/pdc-updater/commit/09575def2
- de3092177 Check state instead of state_name.
  https://github.com/fedora-infra/pdc-updater/commit/de3092177

0.5.2
-----

Commits

- 8481ab695 Get the test suite working again.
  https://github.com/fedora-infra/pdc-updater/commit/8481ab695
- 9200f18be Fix bug in last rebase including modularity stuff.
  https://github.com/fedora-infra/pdc-updater/commit/9200f18be
- 228bc6d8b Merge branch 'modularity-rebased' into develop
  https://github.com/fedora-infra/pdc-updater/commit/228bc6d8b

0.5.1
-----

Commits

- ff39ac395 Include test_modules_data in future release tarballs.
  https://github.com/fedora-infra/pdc-updater/commit/ff39ac395

0.5.0
-----

Pull Requests

- (@ralphbean)      #47, New handler for modularity.
  https://github.com/fedora-infra/pdc-updater/pull/47

Commits

- 0a0566124 Check if the headers are empty.
  https://github.com/fedora-infra/pdc-updater/commit/0a0566124
- 3e89667bb Import unreleased trees into PDC.
  https://github.com/fedora-infra/pdc-updater/commit/3e89667bb
- 9057e2a4a API end points are plural, not singular
  https://github.com/fedora-infra/pdc-updater/commit/9057e2a4a
- fd9e19ab1 Add unit test for tree handler.
  https://github.com/fedora-infra/pdc-updater/commit/fd9e19ab1
- 88ea79c14 Add TmpDir, PushPopD context managers.
  https://github.com/fedora-infra/pdc-updater/commit/88ea79c14
- f5ea16de9 Store module dependencies in PDC.
  https://github.com/fedora-infra/pdc-updater/commit/f5ea16de9
- 83888b093 Filter out stdout of git commands.
  https://github.com/fedora-infra/pdc-updater/commit/83888b093
- c7ddad44a Enhance unit tests for retrieving module metadata.
  https://github.com/fedora-infra/pdc-updater/commit/c7ddad44a
- da336bb08 Add a doc comment to get_or_create_unreleased_variant().
  https://github.com/fedora-infra/pdc-updater/commit/da336bb08
- 84380b657 Document when we expect topdir/tree info in msg.
  https://github.com/fedora-infra/pdc-updater/commit/84380b657
- f44580f6a Process all non-failed module states.
  https://github.com/fedora-infra/pdc-updater/commit/f44580f6a
- fe0cfb41e Use simplified 'name', 'version', 'release' in the message.
  https://github.com/fedora-infra/pdc-updater/commit/fe0cfb41e
- 203c32bfb Build variant_uid from name, version, release.
  https://github.com/fedora-infra/pdc-updater/commit/203c32bfb
- 77e2f8c87 Create koji_tag ourselves.
  https://github.com/fedora-infra/pdc-updater/commit/77e2f8c87
- ac9706e4b Update unit tests for modules for recent changes.
  https://github.com/fedora-infra/pdc-updater/commit/ac9706e4b
- f3c91ed44 More fully qualify our relevant topic suffix.
  https://github.com/fedora-infra/pdc-updater/commit/f3c91ed44
- b12b58df0 Use state_name instead of state.
  https://github.com/fedora-infra/pdc-updater/commit/b12b58df0
- 9182f3d6d Add some debug statements.
  https://github.com/fedora-infra/pdc-updater/commit/9182f3d6d
- 00ed2e597 Correctly submit new unreleased-variants to PDC.
  https://github.com/fedora-infra/pdc-updater/commit/00ed2e597
- fb8c79253 Re-use topic_suffixes here as suggested in review.
  https://github.com/fedora-infra/pdc-updater/commit/fb8c79253
- 4c583061c Rename 'rida' to 'module_build_service'.
  https://github.com/fedora-infra/pdc-updater/commit/4c583061c
- 0add17dc0 User stream/version instead of version/release to synchronise with module build service code
  https://github.com/fedora-infra/pdc-updater/commit/0add17dc0
- 2bd1bfd2f Some appropriate devel settings.
  https://github.com/fedora-infra/pdc-updater/commit/2bd1bfd2f
- dac2e589f PDC expects these to be a dict.
  https://github.com/fedora-infra/pdc-updater/commit/dac2e589f
- 7285e5e11 I swear, PDC expects this value, not the other.
  https://github.com/fedora-infra/pdc-updater/commit/7285e5e11
- d6ce284b0 Whitespace.
  https://github.com/fedora-infra/pdc-updater/commit/d6ce284b0
- dc5560bc0 Convenience for future debugging.
  https://github.com/fedora-infra/pdc-updater/commit/dc5560bc0
- 7238fefe3 Pass deps to PDC in the new style.
  https://github.com/fedora-infra/pdc-updater/commit/7238fefe3
- 5522b0f46 Include ModuleMD in PDC unreleasedvariant and get it from the module.state.change message.
  https://github.com/fedora-infra/pdc-updater/commit/5522b0f46
- c007a7d42 Fix koji_tag - it has to be based on name-stream-version, not just name.
  https://github.com/fedora-infra/pdc-updater/commit/c007a7d42
- 3797021ab Do not add entries to PDC according to Module in 'init' state, because there are not all data in the message in that time
  https://github.com/fedora-infra/pdc-updater/commit/3797021ab
- 2a43a619d Subscribe to both the old and new MBS topics.
  https://github.com/fedora-infra/pdc-updater/commit/2a43a619d
- 7dc6cdbc1 Cleanup unused pieces.
  https://github.com/fedora-infra/pdc-updater/commit/7dc6cdbc1

0.4.10
------

Pull Requests

- (@ralphbean)      #45, Gracefully fail if koji tag doesn't exist.
  https://github.com/fedora-infra/pdc-updater/pull/45

Commits

- 1cd609fcb Gracefully fail if koji tag doesn't exist.
  https://github.com/fedora-infra/pdc-updater/commit/1cd609fcb

0.4.9
-----

Pull Requests

- (@ralphbean)      #43, Flatten the generator so we can check length.
  https://github.com/fedora-infra/pdc-updater/pull/43
- (@mprahl)         #44, Fix traceback occurring when `taskid` is `None`
  https://github.com/fedora-infra/pdc-updater/pull/44

Commits

- a1238ea22 Flatten the generator so we can check length.
  https://github.com/fedora-infra/pdc-updater/commit/a1238ea22
- bd565a123 Use the official Fedora Vagrant box
  https://github.com/fedora-infra/pdc-updater/commit/bd565a123
- 0da773675 Use the `listRPMs` API function
  https://github.com/fedora-infra/pdc-updater/commit/0da773675

0.4.8
-----

Commits

- c89906abf Default value for backwards compat.
  https://github.com/fedora-infra/pdc-updater/commit/c89906abf

0.4.7
-----

Pull Requests

- (@ralphbean)      #34, No need for duplicates here.
  https://github.com/fedora-infra/pdc-updater/pull/34
- (@mprahl)         #35, Pass pdc in as an argument when pdc_tag_mapping is set
  https://github.com/fedora-infra/pdc-updater/pull/35
- (@mprahl)         #37, Fix extract_build_id and clean up test data for Brew builds
  https://github.com/fedora-infra/pdc-updater/pull/37
- (@ralphbean)      #36, Log pre-emptively here.
  https://github.com/fedora-infra/pdc-updater/pull/36
- (@mprahl)         #40, Add compatibility for new error format in PDC
  https://github.com/fedora-infra/pdc-updater/pull/40
- (@mprahl)         #41, Use a retry decorator to account for a lag after an HTTP POST
  https://github.com/fedora-infra/pdc-updater/pull/41
- (@ralphbean)      #39, A second stab at getting the release type right from composes.
  https://github.com/fedora-infra/pdc-updater/pull/39

Commits

- e2ec66e4a No need for duplicates here.
  https://github.com/fedora-infra/pdc-updater/commit/e2ec66e4a
- 2180afb3e Pass pdc in as an argument when pdc_tag_mapping is set
  https://github.com/fedora-infra/pdc-updater/commit/2180afb3e
- 41af82e3f Log pre-emptively here.
  https://github.com/fedora-infra/pdc-updater/commit/41af82e3f
- b51af9dda Fix extract_build_id and clean up test data for Brew builds
  https://github.com/fedora-infra/pdc-updater/commit/b51af9dda
- fdd447f9e A second stab at getting the release type right from composes.
  https://github.com/fedora-infra/pdc-updater/commit/fdd447f9e
- cf2023a71 Add compatibility for new error format in PDC
  https://github.com/fedora-infra/pdc-updater/commit/cf2023a71
- af3ef7d2e Cache this.
  https://github.com/fedora-infra/pdc-updater/commit/af3ef7d2e
- f8bc6c1b0 Merge branch 'develop' of github.com:fedora-infra/pdc-updater into develop
  https://github.com/fedora-infra/pdc-updater/commit/f8bc6c1b0
- 7cf87cc40 Use a retry decorator to account for a lag between an HTTP POST response and when the data is actually available
  https://github.com/fedora-infra/pdc-updater/commit/7cf87cc40

0.4.6
-----

Commits

- d39b9e6a6 Extract the appropriate tag name from the headers here.
  https://github.com/fedora-infra/pdc-updater/commit/d39b9e6a6
- 5380697b3 Bugfix: grab the class name here.
  https://github.com/fedora-infra/pdc-updater/commit/5380697b3
- 8dd01e209 Flatten this to a list so that __contains__ works.
  https://github.com/fedora-infra/pdc-updater/commit/8dd01e209
- dfdaceca3 This is better.
  https://github.com/fedora-infra/pdc-updater/commit/dfdaceca3
- 10f9f676b Merge branch 'feature/generator-schmenerator' into develop
  https://github.com/fedora-infra/pdc-updater/commit/10f9f676b

0.4.5
-----

Commits

- fa64e0332 Some better debugging on not handling messages.
  https://github.com/fedora-infra/pdc-updater/commit/fa64e0332
- 83f3512ca Install libyaml-devel for speed on the test suite.
  https://github.com/fedora-infra/pdc-updater/commit/83f3512ca
- 89fdfb386 Use the container_build_user to find docker builds in a tag.
  https://github.com/fedora-infra/pdc-updater/commit/89fdfb386
- b5c2f36de Merge branch 'feature/yet-more-interesting-tags' into develop
  https://github.com/fedora-infra/pdc-updater/commit/b5c2f36de

0.4.4
-----

Pull Requests

- (@ralphbean)      #30, Gather interesting_tags from PDC if pdc_tag_mapping is True.
  https://github.com/fedora-infra/pdc-updater/pull/30
- (@mprahl)         #29, Parses message-id from internal messages
  https://github.com/fedora-infra/pdc-updater/pull/29

Commits

- 3628d1416 Parses message-id from internal messages
  https://github.com/fedora-infra/pdc-updater/commit/3628d1416
- 9898491d9 Allow configuring which tags different depchain handlers should look for.
  https://github.com/fedora-infra/pdc-updater/commit/9898491d9
- e87223c9a Gather interesting_tags from PDC if pdc_tag_mapping is True.
  https://github.com/fedora-infra/pdc-updater/commit/e87223c9a
- 84993ddd3 Move this filter to the API.
  https://github.com/fedora-infra/pdc-updater/commit/84993ddd3

0.4.3
-----

Pull Requests

- (@mprahl)         #28, Fix construct_topics function typos
  https://github.com/fedora-infra/pdc-updater/pull/28

Commits

- d91b95505 Fix construct_topics function typos
  https://github.com/fedora-infra/pdc-updater/commit/d91b95505

0.4.2
-----

Pull Requests

- (@mprahl)         #23, Change Brew Suffix
  https://github.com/fedora-infra/pdc-updater/pull/23
- (@ralphbean)      #27, Add VCR request data in a compressed tarball.
  https://github.com/fedora-infra/pdc-updater/pull/27
- (@mprahl)         #25, Support STOMP topics without environment
  https://github.com/fedora-infra/pdc-updater/pull/25

Commits

- 37cfa3c0e Change Brew suffix
  https://github.com/fedora-infra/pdc-updater/commit/37cfa3c0e
- d2871b867 Add VCR request data in a compressed tarball.
  https://github.com/fedora-infra/pdc-updater/commit/d2871b867
- dca8db699 Automatically extract cassette dir if it is absent.
  https://github.com/fedora-infra/pdc-updater/commit/dca8db699
- b7e3c875d Make a note about removing the vcr cache for the test suite.
  https://github.com/fedora-infra/pdc-updater/commit/b7e3c875d
- ecaa481c7 Add .idea to .gitignore
  https://github.com/fedora-infra/pdc-updater/commit/ecaa481c7
- 1e885a0b2 Add Vagrant for an easier testing environment
  https://github.com/fedora-infra/pdc-updater/commit/1e885a0b2
- 4b396679b Construct single topic for STOMP connections
  https://github.com/fedora-infra/pdc-updater/commit/4b396679b
- 92c67d09b Raise an exception when zmq and stomp are both enabled
  https://github.com/fedora-infra/pdc-updater/commit/92c67d09b
- 289da7f3f Add unit tests for construct_topic function
  https://github.com/fedora-infra/pdc-updater/commit/289da7f3f

0.4.1
-----

Pull Requests

- (@ralphbean)      #20, Optionally use PDC to map tags to releases.
  https://github.com/fedora-infra/pdc-updater/pull/20
- (@ralphbean)      #22, Backend support for other busses.
  https://github.com/fedora-infra/pdc-updater/pull/22

Commits

- 6f3cb2aa7 Optionally use PDC to map tags to releases.
  https://github.com/fedora-infra/pdc-updater/commit/6f3cb2aa7
- ff70e226c Specfile updates based on review at https://bugzilla.redhat.com/show_bug.cgi?id=1379830
  https://github.com/fedora-infra/pdc-updater/commit/ff70e226c
- 49fd18ed1 Also, provides.
  https://github.com/fedora-infra/pdc-updater/commit/49fd18ed1
- 019b04726 Specfile moved to Fedora dist-git.  http://pkgs.fedoraproject.org/cgit/rpms/pdc-updater
  https://github.com/fedora-infra/pdc-updater/commit/019b04726
- a74ec296a Working on backend support for other busses.
  https://github.com/fedora-infra/pdc-updater/commit/a74ec296a
- 215fca14f Partial progress on the test suite for the other bus backend stuff.
  https://github.com/fedora-infra/pdc-updater/commit/215fca14f
- 4c74ccf46 Get the test suite working again.
  https://github.com/fedora-infra/pdc-updater/commit/4c74ccf46
- 0c0df0d4c Avoid renaming variables, to be less confusing.
  https://github.com/fedora-infra/pdc-updater/commit/0c0df0d4c

0.4.0
-----

Pull Requests

- (@ralphbean)      #16, A stab at modelling container-to-rpm deps.
  https://github.com/fedora-infra/pdc-updater/pull/16
- (@ralphbean)      #17, Revert 16 feature/container deps
  https://github.com/fedora-infra/pdc-updater/pull/17
- (@ralphbean)      #19, Handle 414 error when sanity-checking bulk delete.
  https://github.com/fedora-infra/pdc-updater/pull/19

Commits

- 836a5ca84 Move the base handler out into its own module.
  https://github.com/fedora-infra/pdc-updater/commit/836a5ca84
- 2912b136e Hardcode "interesting" docker tags for now.
  https://github.com/fedora-infra/pdc-updater/commit/2912b136e
- 98f2b6041 A first stab at modelling container<->rpm deps.
  https://github.com/fedora-infra/pdc-updater/commit/98f2b6041
- 07e11a06e Distinguish the component type.
  https://github.com/fedora-infra/pdc-updater/commit/07e11a06e
- 36f8b5da4 Fix a mock in old tests.
  https://github.com/fedora-infra/pdc-updater/commit/36f8b5da4
- 0f19feafc Check this.. a vcr record was driving me crazy here.
  https://github.com/fedora-infra/pdc-updater/commit/0f19feafc
- d5b3ccbd7 Update the test suite.
  https://github.com/fedora-infra/pdc-updater/commit/d5b3ccbd7
- a53dc7c18 Fix a loop bug.
  https://github.com/fedora-infra/pdc-updater/commit/a53dc7c18
- 73e8c465e Rename this function to better reflect what it does.
  https://github.com/fedora-infra/pdc-updater/commit/73e8c465e
- c17d74628 Some more renaming, just to get the semantics right.
  https://github.com/fedora-infra/pdc-updater/commit/c17d74628
- e056bba20 Get audit/init working for containers.
  https://github.com/fedora-infra/pdc-updater/commit/e056bba20
- 2751391c6 Tests for the container depchain handler.
  https://github.com/fedora-infra/pdc-updater/commit/2751391c6
- 6ca07008a Move this rpm-centric code into an intermediary base class.
  https://github.com/fedora-infra/pdc-updater/commit/6ca07008a
- eadf64793 Typofix.
  https://github.com/fedora-infra/pdc-updater/commit/eadf64793
- 6a60b4524 Handle possible error here.
  https://github.com/fedora-infra/pdc-updater/commit/6a60b4524
- 6b406b2aa Revert "A stab at modelling container-to-rpm deps."
  https://github.com/fedora-infra/pdc-updater/commit/6b406b2aa
- c55a42feb Revert "Revert "A stab at modelling container-to-rpm deps.""
  https://github.com/fedora-infra/pdc-updater/commit/c55a42feb
- ddaae3704 Fix atomic git url at @puiterwijk's suggestion.
  https://github.com/fedora-infra/pdc-updater/commit/ddaae3704
- 6617cdaa0 Handle 414 error when sanity-checking bulk delete.
  https://github.com/fedora-infra/pdc-updater/commit/6617cdaa0
- 46ae92038 Require fedmsg-hub.
  https://github.com/fedora-infra/pdc-updater/commit/46ae92038

0.3.1
-----

Commits

- e769f842c Just make this an in-memory cache.
  https://github.com/fedora-infra/pdc-updater/commit/e769f842c
- eda374130 40,000 is a lot less than 120,000
  https://github.com/fedora-infra/pdc-updater/commit/eda374130

0.3.0
-----

Pull Requests

- (@ralphbean)      #7, Apply with_ridiculous_timeout to the _import_compose method.
  https://github.com/fedora-infra/pdc-updater/pull/7
- (@ralphbean)      #8, Pretend like kojipkgs has what we expect.
  https://github.com/fedora-infra/pdc-updater/pull/8
- (@ralphbean)      #12, Not all composes have RPMS.
  https://github.com/fedora-infra/pdc-updater/pull/12
- (@nphilipp)       #13, use PDCClient.get_paged()
  https://github.com/fedora-infra/pdc-updater/pull/13
- (@ralphbean)      #15, Introducing new handlers to maintain an rpm dep chain.
  https://github.com/fedora-infra/pdc-updater/pull/15

Commits

- fa305cd52 Demote this log statement.
  https://github.com/fedora-infra/pdc-updater/commit/fa305cd52
- 608d70814 Sleeping beauty.
  https://github.com/fedora-infra/pdc-updater/commit/608d70814
- 8afdbc121 Forgotten import.
  https://github.com/fedora-infra/pdc-updater/commit/8afdbc121
- 258c606f9 Check to make sure a compose is really really done before considering it.
  https://github.com/fedora-infra/pdc-updater/commit/258c606f9
- ac130f8b7 First stab at a diagram.
  https://github.com/fedora-infra/pdc-updater/commit/ac130f8b7
- a2be25f57 build diagram.
  https://github.com/fedora-infra/pdc-updater/commit/a2be25f57
- d9c51edb5 Klaxon.
  https://github.com/fedora-infra/pdc-updater/commit/d9c51edb5
- 23e9fb360 s/fedorainfracloud/fedoraproject/g
  https://github.com/fedora-infra/pdc-updater/commit/23e9fb360
- 52325526a We don't need the --insecure option anymore.
  https://github.com/fedora-infra/pdc-updater/commit/52325526a
- 271810f5b libyaml-devel makes the tests 10x faster.
  https://github.com/fedora-infra/pdc-updater/commit/271810f5b
- 956c2b0b5 atomic: Remove a duplicate component-groups query
  https://github.com/fedora-infra/pdc-updater/commit/956c2b0b5
- 19eca57a6 Allow in both FINISHED and FINISHED_INCOMPLETE composes.
  https://github.com/fedora-infra/pdc-updater/commit/19eca57a6
- fe906113f 0.2.4
  https://github.com/fedora-infra/pdc-updater/commit/fe906113f
- 9792b18b0 Merge branch 'master' into develop
  https://github.com/fedora-infra/pdc-updater/commit/9792b18b0
- f98249fd7 specbump
  https://github.com/fedora-infra/pdc-updater/commit/f98249fd7
- 23ef90842 pdc-client will be in the buildroot someday soon...
  https://github.com/fedora-infra/pdc-updater/commit/23ef90842
- 9a1c26b93 Disable tests for now until we get pdc-client in the buildroot.
  https://github.com/fedora-infra/pdc-updater/commit/9a1c26b93
- 9348dd98b Note to self.
  https://github.com/fedora-infra/pdc-updater/commit/9348dd98b
- f2903804e More info in this error message, please.
  https://github.com/fedora-infra/pdc-updater/commit/f2903804e
- 84bced32c Error check on this request.
  https://github.com/fedora-infra/pdc-updater/commit/84bced32c
- a60cbd6ae Better error message this way..
  https://github.com/fedora-infra/pdc-updater/commit/a60cbd6ae
- 497fb0fcb Actually, this is not our problem.  This is the atomic devs problem.
  https://github.com/fedora-infra/pdc-updater/commit/497fb0fcb
- 73e6cdf18 Move the with_ridiculous_timeout decorator to the utils module.
  https://github.com/fedora-infra/pdc-updater/commit/73e6cdf18
- a91688d45 Apply with_ridiculous_timeout to the _import_compose method.
  https://github.com/fedora-infra/pdc-updater/commit/a91688d45
- eddba65ba Pretend like kojipkgs has what we expect.
  https://github.com/fedora-infra/pdc-updater/commit/eddba65ba
- c438a39ba This was backwards.
  https://github.com/fedora-infra/pdc-updater/commit/c438a39ba
- 0e63cf430 Some fixes for the failing test suite (sloppy threebean..)
  https://github.com/fedora-infra/pdc-updater/commit/0e63cf430
- c89994892 Not all composes have RPMS.
  https://github.com/fedora-infra/pdc-updater/commit/c89994892
- c15ee8852 use PDCClient.get_paged()
  https://github.com/fedora-infra/pdc-updater/commit/c15ee8852
- 5864fca6f Tests for new rpm depchain handlers.
  https://github.com/fedora-infra/pdc-updater/commit/5864fca6f
- 3334d7a62 New depchain handlers for RPM.
  https://github.com/fedora-infra/pdc-updater/commit/3334d7a62
- 885aadae6 Update our utilities to support the new rpm depchain handlers.
  https://github.com/fedora-infra/pdc-updater/commit/885aadae6
- 8caec5d18 Fix config paths.
  https://github.com/fedora-infra/pdc-updater/commit/8caec5d18
- 2546dfc55 Link to the wiki page.
  https://github.com/fedora-infra/pdc-updater/commit/2546dfc55
- 675decc11 Encapsulate this PDC query, and fix a bug.
  https://github.com/fedora-infra/pdc-updater/commit/675decc11
- 2992a392e Prune the graph when deps disappear in koji.
  https://github.com/fedora-infra/pdc-updater/commit/2992a392e
- fe9306aec Replace pprint with log.warn as per review discussion.
  https://github.com/fedora-infra/pdc-updater/commit/fe9306aec
- 921afbc3e Re-use topic_suffixes to reduce hardcoding.
  https://github.com/fedora-infra/pdc-updater/commit/921afbc3e
- f6d892de1 Use an f24 build instead of f26 to get the test suite consistent again.
  https://github.com/fedora-infra/pdc-updater/commit/f6d892de1
- 2fc8d098f Set managed_types to None in the base class.
  https://github.com/fedora-infra/pdc-updater/commit/2fc8d098f
- 597a80503 Fix up some naming, as per @PrahlM93's recommendations.
  https://github.com/fedora-infra/pdc-updater/commit/597a80503
- 9e87f4fcd Fix copy/pasta.
  https://github.com/fedora-infra/pdc-updater/commit/9e87f4fcd
- 1a83083d6 More tag/mock wrangling.
  https://github.com/fedora-infra/pdc-updater/commit/1a83083d6
- d99d438b3 Finish implementing the graph pruning logic.
  https://github.com/fedora-infra/pdc-updater/commit/d99d438b3
- a84dcf3db Fix erroneous API parameter usage.
  https://github.com/fedora-infra/pdc-updater/commit/a84dcf3db
- 555fd39a3 The results list here has a dict envelope around it.
  https://github.com/fedora-infra/pdc-updater/commit/555fd39a3
- 8d198595d Fix this API invocation and handle the error we now know to expect.
  https://github.com/fedora-infra/pdc-updater/commit/8d198595d
- d748b058a Eliminate a number of unnecessary checks and API calls.
  https://github.com/fedora-infra/pdc-updater/commit/d748b058a
- f518728c4 Some logging.
  https://github.com/fedora-infra/pdc-updater/commit/f518728c4
- f6954f464 Move this managed check inside the generator.
  https://github.com/fedora-infra/pdc-updater/commit/f6954f464
- a9b1c602a Make the audit method much simpler.
  https://github.com/fedora-infra/pdc-updater/commit/a9b1c602a
- 7cc9c23d9 Rename these to be more specific (we're going to add more...)
  https://github.com/fedora-infra/pdc-updater/commit/7cc9c23d9
- 7f529f502 Refactor the depchain stuff to use bulk operations.
  https://github.com/fedora-infra/pdc-updater/commit/7f529f502
- 8794bd96e Be polite.
  https://github.com/fedora-infra/pdc-updater/commit/8794bd96e
- de6f1d2f8 Fix a bug in bulk delete where the release_id was never extracted.
  https://github.com/fedora-infra/pdc-updater/commit/de6f1d2f8
- a136836bf Remove erroneous duplicate queries to koji during initialization.
  https://github.com/fedora-infra/pdc-updater/commit/a136836bf
- da296849e Link to this improved message hook code.
  https://github.com/fedora-infra/pdc-updater/commit/da296849e
- 1ddd02500 More clear logging about progress.
  https://github.com/fedora-infra/pdc-updater/commit/1ddd02500
- 7399f7391 Use the SRPM name here.
  https://github.com/fedora-infra/pdc-updater/commit/7399f7391
- 7723a2049 Add retry logic to protect ourselves from temporary network blips.
  https://github.com/fedora-infra/pdc-updater/commit/7723a2049
- b388f033f Drop parent consolidation so initialize can import on the fly.
  https://github.com/fedora-infra/pdc-updater/commit/b388f033f
- 8c9879199 Ensure this PK exists.
  https://github.com/fedora-infra/pdc-updater/commit/8c9879199
- 7e87aea1d Adjust logging.
  https://github.com/fedora-infra/pdc-updater/commit/7e87aea1d
- 35b103c75 Utilities for chunked queries.
  https://github.com/fedora-infra/pdc-updater/commit/35b103c75
- dcaae2dba Only make this query once.
  https://github.com/fedora-infra/pdc-updater/commit/dcaae2dba
- 75d48b553 Less logging.
  https://github.com/fedora-infra/pdc-updater/commit/75d48b553
- 07c3e9ca3 Use chunked query for bulk release component relationships.
  https://github.com/fedora-infra/pdc-updater/commit/07c3e9ca3
- 2db0fdb17 Further work on de-duplication.
  https://github.com/fedora-infra/pdc-updater/commit/2db0fdb17
- 2741f2de4 Apply chunked queries to other bulk functions.
  https://github.com/fedora-infra/pdc-updater/commit/2741f2de4
- 98d93a16a Get arch handling correct.
  https://github.com/fedora-infra/pdc-updater/commit/98d93a16a
- 4082d575e Nice to do modern tags first.
  https://github.com/fedora-infra/pdc-updater/commit/4082d575e
- 5d1b275b5 Unused.
  https://github.com/fedora-infra/pdc-updater/commit/5d1b275b5
- b68685bb4 Kill TODO.txt.
  https://github.com/fedora-infra/pdc-updater/commit/b68685bb4
- a0afe6dc6 Use threads to query koji in parallel.
  https://github.com/fedora-infra/pdc-updater/commit/a0afe6dc6
- 73a9a68b3 Finish out the last chunk of the loop.
  https://github.com/fedora-infra/pdc-updater/commit/73a9a68b3
- 261e4411e We make more calls to PDC now (less calls to koji).
  https://github.com/fedora-infra/pdc-updater/commit/261e4411e
- 87513cd48 Disable sanity checks for now.
  https://github.com/fedora-infra/pdc-updater/commit/87513cd48
- 2c8336cfa Update our test mocks.
  https://github.com/fedora-infra/pdc-updater/commit/2c8336cfa
- 4e08b514c Merge branch 'feature/rpm-dep-chain' into develop
  https://github.com/fedora-infra/pdc-updater/commit/4e08b514c
- 9da65cb6c Add some retry logic for weird koji session behavior.
  https://github.com/fedora-infra/pdc-updater/commit/9da65cb6c
- c6d7383c6 Fix mocks, yet again.
  https://github.com/fedora-infra/pdc-updater/commit/c6d7383c6

0.2.4
-----

Pull Requests

- (@lmacken)        #2, s/fedorainfracloud/fedoraproject/g
  https://github.com/fedora-infra/pdc-updater/pull/2
- (@lmacken)        #3, We don't need the --insecure option anymore.
  https://github.com/fedora-infra/pdc-updater/pull/3
- (@ralphbean)      #5, libyaml-devel makes the tests 10x faster.
  https://github.com/fedora-infra/pdc-updater/pull/5
- (@lmacken)        #4, atomic: Remove a duplicate component-groups query
  https://github.com/fedora-infra/pdc-updater/pull/4
- (@ralphbean)      #6, Allow in both FINISHED and FINISHED_INCOMPLETE composes.
  https://github.com/fedora-infra/pdc-updater/pull/6

Commits

- 22d8bbc3b Demote this log statement.
  https://github.com/fedora-infra/pdc-updater/commit/22d8bbc3b
- c2917594d Sleeping beauty.
  https://github.com/fedora-infra/pdc-updater/commit/c2917594d
- 2f3517852 Forgotten import.
  https://github.com/fedora-infra/pdc-updater/commit/2f3517852
- 7c4b045d7 Check to make sure a compose is really really done before considering it.
  https://github.com/fedora-infra/pdc-updater/commit/7c4b045d7
- eff32fa0b First stab at a diagram.
  https://github.com/fedora-infra/pdc-updater/commit/eff32fa0b
- 689c54949 build diagram.
  https://github.com/fedora-infra/pdc-updater/commit/689c54949
- b046ac7d9 Klaxon.
  https://github.com/fedora-infra/pdc-updater/commit/b046ac7d9
- 49a5e5d2d s/fedorainfracloud/fedoraproject/g
  https://github.com/fedora-infra/pdc-updater/commit/49a5e5d2d
- c06e2e4ae We don't need the --insecure option anymore.
  https://github.com/fedora-infra/pdc-updater/commit/c06e2e4ae
- 9105bd6c2 atomic: Remove a duplicate component-groups query
  https://github.com/fedora-infra/pdc-updater/commit/9105bd6c2
- bf2f59566 libyaml-devel makes the tests 10x faster.
  https://github.com/fedora-infra/pdc-updater/commit/bf2f59566
- 8ffdf3ccf Allow in both FINISHED and FINISHED_INCOMPLETE composes.
  https://github.com/fedora-infra/pdc-updater/commit/8ffdf3ccf

0.2.3
-----

Commits

- 6020cfcf2 Fix the pkgdb audit code.
  https://github.com/fedora-infra/pdc-updater/commit/6020cfcf2
- ddc8a7d41 Use a common requests session.
  https://github.com/fedora-infra/pdc-updater/commit/ddc8a7d41
- c51fa8954 Use mdapi to map atomic components to parent srpms.
  https://github.com/fedora-infra/pdc-updater/commit/c51fa8954
- e947678dc specbump.
  https://github.com/fedora-infra/pdc-updater/commit/e947678dc

0.2.2
-----

Commits

- 68895bcfc specbump.
  https://github.com/fedora-infra/pdc-updater/commit/68895bcfc
- 15c4017ea Not true anymore.
  https://github.com/fedora-infra/pdc-updater/commit/15c4017ea
- b82e2c5a7 Some more descriptive text.
  https://github.com/fedora-infra/pdc-updater/commit/b82e2c5a7
- 8e89162bf Update the audit script to handle atomic group discrepancies.
  https://github.com/fedora-infra/pdc-updater/commit/8e89162bf
- fbfac07b3 specbump.
  https://github.com/fedora-infra/pdc-updater/commit/fbfac07b3

0.2.1
-----

Commits

- 52bd663d2 specbump.
  https://github.com/fedora-infra/pdc-updater/commit/52bd663d2
- cad29ef33 Get rid of all the bulk-insert actions.  They timeout.
  https://github.com/fedora-infra/pdc-updater/commit/cad29ef33

0.2.0
-----

Commits

- 1d252ce44 1.1.1
  https://github.com/fedora-infra/pdc-updater/commit/1d252ce44
- d1851facb Some fixes from staging.
  https://github.com/fedora-infra/pdc-updater/commit/d1851facb
- d4b3b2cc4 Drop the base product stuff.  Don't need it.
  https://github.com/fedora-infra/pdc-updater/commit/d4b3b2cc4
- c7776de27 First pass at atomic components.
  https://github.com/fedora-infra/pdc-updater/commit/c7776de27
- a4ad0d650 We're doing this now.
  https://github.com/fedora-infra/pdc-updater/commit/a4ad0d650
- 427fedbee Use group_pk when updating a component group.
  https://github.com/fedora-infra/pdc-updater/commit/427fedbee
- 0f1c9e271 log when done initializing.
  https://github.com/fedora-infra/pdc-updater/commit/0f1c9e271
- b78401203 Get the atomic group manager to handle multiple releases.
  https://github.com/fedora-infra/pdc-updater/commit/b78401203
- 2f5b23b0c Some tests for the atomic components stuff.
  https://github.com/fedora-infra/pdc-updater/commit/2f5b23b0c
- aba5fe38c Merge branch 'feature/atomic-components' into develop
  https://github.com/fedora-infra/pdc-updater/commit/aba5fe38c

0.1.1
-----

Commits

- 4dcf8961f Remove unusable pkgdb API call.
  https://github.com/fedora-infra/pdc-updater/commit/4dcf8961f
- bde941d19 Update tests accordingly.
  https://github.com/fedora-infra/pdc-updater/commit/bde941d19
- 516e9ae78 Merge branch 'feature/unusable-pkgdb-call' into develop
  https://github.com/fedora-infra/pdc-updater/commit/516e9ae78
