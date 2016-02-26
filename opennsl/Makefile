all: pull

pull:
	@git clone https://github.com/Broadcom-Switch/OpenNSL.git
	@cd OpenNSL/ && git checkout 8e0b499f02dcef751a3703c9a18600901374b28a

install:
	@mkdir -p $(DESTDIR)/lib
	@cp -r OpenNSL/bin/wedge-trident/* $(DESTDIR)/lib/
