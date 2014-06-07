#export PATH=/home/me/.gem/ruby/2.1.0/bin:$PATH
cd negative;
for i in {41..80}; do
	echo $i;
	twurl '/1.1/search/tweets.json?q=:(&lang=ru&count=100&result_type=recent' > "request_$i";
	echo "received";
	sleep 90;
done;
