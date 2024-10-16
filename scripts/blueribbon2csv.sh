#!sh
echo 'NAME, LATITUDE, LONGITUDE, ADDRESS' > blueribbon.csv
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-5]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=01.%20%EC%A0%9C%EC%A3%BC%EC%8B%9C&zone2Lat=33.50003088481452&zone2Lng=126.52994590199417' | jq --raw-output '._embedded.restaurants.[] | [.headerInfo.nameKR, .gps.latitude, .gps.longitude, "\(.juso.roadAddrPart1) \(.juso.roadAddrPart2)"] | @csv' >> blueribbon.csv

echo './blueribbon.csv'
