#![no_main]
#![no_std]

extern crate panic_halt as _;
use earlgrey_pac::Peripherals;
use riscv_rt::entry;

#[entry]
fn main() -> ! {
    let p = Peripherals::take().unwrap();
    let uart = p.UART0;
    loop {}
}
