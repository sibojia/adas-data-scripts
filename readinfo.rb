require 'json'

file_list = ARGV[0]
data = {}
File.readlines(file_list).each do |line|
	s = File.read(line.chomp)
	j = JSON.parse(s)
	if j['Rects']
		data[j['ImagePath']] = j['Rects'].map {|r| [r['x'], r['y'], r['width'], r['height']]}
	else
		data[j['ImagePath']] = []
	end
end
sorted = data.sort
File.open(ARGV[1], 'w') do |f|
	sorted.each do |item|
		f.puts "#{item[1].size}"
		item[1].each {|i| f.puts(i.map(&:to_i).join " ")}
	end
end
