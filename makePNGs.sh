for pic in images/*;
do
	#if  [ $pic =~ "[a-zA-Z0-9]*[.]png" ]
	if  ! [[ $pic == *.png ]]
	then
		echo $pic
		y=${pic%.*}
		base=${y##*/}
		convert $pic "images/$base.png"
		rm -f $pic
	fi
done
