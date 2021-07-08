import dashboard_compile, sys
sys.path.append('/Users/patrick/PycharmProjects/FortressWork/ConstraintsReportBuilder')
import constraints_main, constraints_factors

def main():
    print("FORE")
    m, listo, maxes, mins = constraints_main.main()
    dashboard_compile.compile(m, listo, maxes, mins)

if __name__ == '__main__':
    main()