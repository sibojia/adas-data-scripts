require 'json'
require 'find'

labeldir = ARGV[0]
data = {}
Find.find("#{labeldir}/Label/").each do |path|
	next if FileTest.directory?(path)
	s = File.read(path.chomp)
	j = JSON.parse(s)
	if j['Rects']
		data[j['ImagePath']] = j['Rects'].map {|r| [r['x'], r['y'], r['width'], r['height']]}
	else
		data[j['ImagePath']] = []
	end
end
sorted = []
File.open("#{labeldir}/GuidMapping.txt").readlines().map { |e|
	name = e.chomp.split('"')[0]
	if data[name]
		sorted << data[name]
	else
		sorted << []
	end
}

File.open(ARGV[1], 'w') do |f|
	sorted.each do |item|
		f.puts "#{item.size}"
		item.each {|i| f.puts(i.map(&:to_i).join " ")}
	end
end
