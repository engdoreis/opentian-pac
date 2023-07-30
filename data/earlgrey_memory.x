MEMORY {
  rom(rx)             : ORIGIN = 0x00008000, LENGTH = 0x8000
  ram_main(rwx)       : ORIGIN = 0x10000000, LENGTH = 0x20000
  eflash(rx)          : ORIGIN = 0x20000000, LENGTH = 0x100000
  ram_ret_aon(rwx)    : ORIGIN = 0x40600000, LENGTH = 0x1000
}
