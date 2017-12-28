from .user import User
from .package import (Package,
                      package_schema, packages_schema)
from .package_suite import (PackageSuite,
                            package_suite_schema, package_suites_schema)
from .namespace import (Namespace,
                        namespace_schema, namespaces_schema)
from .package_version import (PackageVersion,
                              package_versions_schema, package_version_schema,
                              package_with_versions_schema)
from .release import Release, release_manifest_schema
from .scheduled_release import ScheduledRelease


assert(User)

assert(Package)
assert(Namespace)
assert(packages_schema)
assert(package_schema)
assert(namespace_schema)
assert(namespaces_schema)

assert(PackageSuite)
assert(package_suite_schema)
assert(package_suites_schema)

assert(PackageVersion)
assert(package_versions_schema)
assert(package_version_schema)
assert(package_with_versions_schema)

assert(Release)
assert(release_manifest_schema)

assert(ScheduledRelease)
