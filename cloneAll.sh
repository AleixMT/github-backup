while IFS= read -r line; do 
   git clone "${line}"
done < file.txt
