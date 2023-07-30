#![no_std]
#![allow(non_camel_case_types)]

pub use earlgrey_pac::generic::*;
pub use earlgrey_pac::*;

include!(concat!(env!("OUT_DIR"), "/lib.rs"));
