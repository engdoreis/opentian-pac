use std::env;
use std::fs;
use std::process::Command;

use svd2rust::{Config, Target};

const TOP_NAME: &str = "earlgrey";

fn main() {
    let out = env::var("OUT_DIR").unwrap();

    svd_to_rust(&out);

    generate_linker_script(&out);
}

// Put the memory layout file where the linker can find it.
fn generate_linker_script(out: &str) {
    let mut content = fs::read_to_string(format!("../data/{TOP_NAME}_memory.x")).unwrap();
    content.push_str(&fs::read_to_string("memory_alias.x").unwrap());
    fs::write(format!("{out}/{TOP_NAME}_memory.x"), content).unwrap();
    println!("cargo:rustc-link-search={out}");
    println!("cargo:rerun-if-changed=../data/{TOP_NAME}_memory.x");
}

fn svd_to_rust(out: &str) {
    let svd = fs::read_to_string(format!("../data/{TOP_NAME}.svd")).unwrap();
    let config = Config {
        target: Target::RISCV,
        pascal_enum_values: true,
        make_mod: true,
        ..Default::default()
    };

    let generated = svd2rust::generate(&svd, &config).unwrap();

    let out_file = format!("{out}/{TOP_NAME}_pac.rs");
    fs::write(&out_file, generated.lib_rs).unwrap();

    let _ = Command::new("rustfmt").arg(out_file).status();

    fs::write(
        format!("{out}/lib.rs"),
        format!(r#"#[path="{out}/{TOP_NAME}_pac.rs"] mod {TOP_NAME}_pac;"#),
    )
    .unwrap();
    println!("cargo:rerun-if-changed=../data/{TOP_NAME}.svd");
}
