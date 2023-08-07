import argparse
from tools.main_skyscanner_scrapper import SkyscannerScrapper_plan
import datetime

def main():
    parser = argparse.ArgumentParser(description='Skyscanner Scraper - Trip Plan')
    parser.add_argument('takeoff_location', type=str, help='The takeoff_location for trip plan (e.g., tpet)')
    parser.add_argument('land_location', type=str, help='The land_location for trip plan (e.g., hkd)')
    parser.add_argument('go_plan_date', type=str, help='The date for trip plan (e.g., 231201)')
    args = parser.parse_args()

    takeoff_location = args.takeoff_location
    land_location = args.land_location
    go_plan_date = args.go_plan_date

    createtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    SkyscannerScraper = SkyscannerScrapper_plan()
    trip_info = SkyscannerScraper.scrape_trip_plan(takeoff_location, land_location, go_plan_date)
    SkyscannerScraper.trip_plan_memo(trip_info, createtime)
    SkyscannerScraper.trip_plan_detail(trip_info, go_plan_date, createtime)

if __name__ == '__main__':
    main()
