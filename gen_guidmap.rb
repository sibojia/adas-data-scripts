require 'find'
require 'securerandom'

IMG_EXT = %w(.jpg .jpeg .png .bmp)

def new_uuid
    SecureRandom.uuid.gsub(/-/, '')
end

fout = File.open(ARGV[1], 'w')
root_path = ARGV[0]
root_path += '/' if root_path[-1] != '/'
Find.find(root_path) do |path|
	if IMG_EXT.include? File.extname(path)
		fout.puts "#{path.sub(root_path, '')}\"#{new_uuid}"
	end
end
