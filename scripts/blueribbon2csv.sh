#!sh
# 1. go www.bluer.co.kr
# 2. select jeju from search by region
# 3. open 01. jeju-si
# 4. find request url from developer tool
# 5. repeat for other regions

function parse2csv() {
  jq --raw-output '._embedded.restaurants.[] | [.headerInfo.nameKR, .gps.latitude, .gps.longitude, "\(.juso.roadAddrPart1) \(.juso.roadAddrPart2)"] | @csv'
}

TMPFILE=$(mktemp)

curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-5]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=01.%20%EC%A0%9C%EC%A3%BC%EC%8B%9C&zone2Lat=33.50003088481452&zone2Lng=126.52994590199417' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-2]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=02.%20%EC%A0%9C%EC%A3%BC%EC%8B%9C%28%EC%8B%A0%EC%8B%9C%EA%B0%80%EC%A7%80%29&zone2Lat=33.490126467623995&zone2Lng=126.4939008483177' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=0&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=03.%20%EC%A0%9C%EC%A3%BC%EC%8B%9C%28%EC%95%A0%EC%9B%94%29&zone2Lat=33.462013721757444&zone2Lng=126.32885811868633' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-1]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=04.%20%EC%A0%9C%EC%A3%BC%EC%8B%9C%28%ED%95%9C%EB%A6%BC%29&zone2Lat=33.408743150371926&zone2Lng=126.26807871947138' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-1]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=04.%20%EC%A0%9C%EC%A3%BC%EC%8B%9C%28%ED%95%9C%EB%A6%BC%29&zone2Lat=33.408743150371926&zone2Lng=126.26807871947138' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=0&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=06.%20%EC%A0%9C%EC%A3%BC%EC%8B%9C%28%EC%84%B8%ED%99%94%2F%EA%B9%80%EB%85%95%2F%EA%B5%AC%EC%A2%8C%29&zone2Lat=33.55542693457876&zone2Lng=126.75042480384563' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-1]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=07.%20%EC%84%B1%EC%82%B0%2F%EC%9A%B0%EB%8F%84&zone2Lat=33.4683628977731&zone2Lng=126.931864034662' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-2]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=08.%20%EC%84%9C%EA%B7%80%ED%8F%AC%EC%8B%9C&zone2Lat=33.24660011583679&zone2Lng=126.56291015472402' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-1]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=09.%20%EC%84%9C%EA%B7%80%ED%8F%AC%EC%8B%9C%28%EC%A4%91%EB%AC%B8%29&zone2Lat=33.24982753641955&zone2Lng=126.42381542197339' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-1]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=10.%20%EC%84%9C%EA%B7%80%ED%8F%AC%EC%8B%9C%28%EB%82%A8%EC%9B%90%2F%ED%91%9C%EC%84%A0%29&zone2Lat=33.27289907267224&zone2Lng=126.68453698330696' | parse2csv >> $TMPFILE
curl -s 'https://www.bluer.co.kr/api/v1/restaurants?page=[0-1]&size=30&query=&foodType=&foodTypeDetail=&feature=&location=&locationDetail=&area=&areaDetail=&priceRange=&ribbonType=&recommended=false&listType=list&isSearchName=false&tabMode=single&searchMode=map&zone1=%EC%A0%9C%EC%A3%BC&zone2=11.%20%EC%84%9C%EA%B7%80%ED%8F%AC%EC%8B%9C%28%EB%8C%80%EC%A0%95%2F%EC%95%88%EB%8D%95%29&zone2Lat=33.2229604971036&zone2Lng=126.27450806694' | parse2csv >> $TMPFILE


echo 'NAME,LATITUDE,LONGITUDE,ADDRESS' > blueribbon.csv
sort $TMPFILE | uniq >> blueribbon.csv # remove duplicate
echo './blueribbon.csv'
