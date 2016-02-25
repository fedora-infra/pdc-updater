
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
