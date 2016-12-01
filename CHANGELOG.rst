
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
