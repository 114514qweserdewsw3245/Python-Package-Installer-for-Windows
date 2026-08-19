"""Start Python-Package-Installer-for-Windows Agent V0.7.5."""
from agent.catalog_migration import restore_packages_json
from agent.installer import main
if __name__ == "__main__":
    result = restore_packages_json()
    action = "restored" if result["restored"] else "verified"
    print(f"Package catalogue {action}: {result['packages']} packages in {result['categories']} categories.")
    main()
