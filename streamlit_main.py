import dashboard_compile, sys
sys.path.append('/Users/patrick/PycharmProjects/FortressWork/DashboardData')
import dashboard_data_main

def main():
    print("FORE")
    items = dashboard_data_main.main()
    dashboard_compile.compile(items)

if __name__ == '__main__':
    main()