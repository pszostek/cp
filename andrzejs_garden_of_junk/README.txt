usage:
	./cp_perf report --stdio

produces:
	process csv
	dso csv
	sample data

writing sample data:
	# LBR
	# write zero record to separate groups. later zeroes appear also in from/to and such records can be removed
        rval = fwrite(&zero, sizeof(thr->pid), 1, f);
        rval = fwrite(&zero, sizeof(bi[i].from.al_addr), 1, f);
        rval = fwrite(&zero, sizeof(bi[i].from.map->dso->id), 1, f);
        rval = fwrite(&zero, sizeof(bi[i].to.al_addr), 1, f);
        rval = fwrite(&zero, sizeof(bi[i].to.map->dso->id), 1, f);
	for i = #branches to 0: 
                        rval = fwrite(&thr->pid, sizeof(thr->pid), 1, f);
                        rval = fwrite(&bi[i].from.al_addr, sizeof(bi[i].from.al_addr), 1, f);
                        rval = fwrite(&bi[i].from.map->dso->id, sizeof(bi[i].from.map->dso->id), 1, f);
                        rval = fwrite(&bi[i].to.al_addr, sizeof(bi[i].to.al_addr), 1, f);
                        rval = fwrite(&bi[i].to.map->dso->id, sizeof(bi[i].to.map->dso->id), 1, f);


	# EBS
        rval = fwrite(&thread->pid, sizeof(thread->pid), 1, f);
        rval = fwrite(&al->map->dso->id, sizeof(al->map->dso->id), 1, f);
        rval = fwrite(&al->addr, sizeof(al->addr), 1, f);


reading sample data:
	# LBR
	import np as numpy	
	dt = np.dtype([("tid", "int32"), ("from_a", "int64"), ("from_dso", "uint32"), ("to_a", "int64"), ("to_dso", "uint32")])
	x = np.fromfile(fname, dtype=dt)

	# EBS
	import np as numpy
	dt = np.dtype([("tid", "int32"), ("dso", "uint32"), ("ip", "uint64")])
	y = np.fromfile(fname, dtype=dt)
