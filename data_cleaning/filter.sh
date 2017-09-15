
files=`ls`

for f in *pdf; do
	count=`file $f |grep 'PDF'|wc -l`
	if [ ${count} -eq 0 ];then
		echo $f" is corrupted" >> corrupt_log.txt
		#cp $f ".."
		file $f >> corrupt_log.txt
		mv $f "../corrupted_pdfs"
	fi
done
