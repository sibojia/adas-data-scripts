import sys, os
sys.path.append(os.getcwd() + '/../')
import google.protobuf
import caffe.proto.caffe_pb2 as caffe_pb2

def addsuffix_model(proto, suffix, startlayer = None):
    fromstart=False
    suffix='_'+suffix
    if startlayer is None:
        fromstart=True
    for layer in proto.layer:
        if fromstart:
            layer.name = layer.name + suffix
            for i,b in enumerate(layer.bottom):
                layer.bottom[i]=b+suffix
            for i,t in enumerate(layer.top):
                layer.top[i]=t+suffix
        if fromstart == False and layer.name == startlayer: fromstart = True

def addsuffix_file(inp, outp, suffix, startlayer = None):
    proto=caffe_pb2.NetParameter()
    basename = os.path.basename(inp)
    if 'model' in basename:
        proto.ParseFromString(open(inp).read())
    else:
        google.protobuf.text_format.Merge(open(inp).read(), proto)
    addsuffix_model(proto, suffix, startlayer)
    if 'model' in basename:
        open(outp,'wb').write(proto.SerializeToString())
    else:
        open(outp,'w').write(google.protobuf.text_format.MessageToString(proto))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'Usage: addsuffix.py input, output, suffix, [startlayer]'
        exit(-1)
    addsuffix_file(*sys.argv[1:])
    print 'done'
