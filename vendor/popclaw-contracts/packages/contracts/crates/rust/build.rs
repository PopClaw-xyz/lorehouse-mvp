use std::path::PathBuf;

fn main() {
    let out = PathBuf::from("src/generated");
    std::fs::create_dir_all(&out).expect("create src/generated");

    let protos = [
        "../../proto/identity.proto",
        "../../proto/event.proto",
        "../../proto/invite.proto",
        "../../proto/quest.proto",
        "../../proto/profile.proto",
        "../../proto/house_session.proto",
        "../../proto/world_interaction.proto",
        "../../proto/public_stream.proto",
    ];
    for p in &protos {
        println!("cargo:rerun-if-changed={p}");
    }
    println!("cargo:rerun-if-changed=build.rs");

    prost_build::Config::new()
        .out_dir(&out)
        .btree_map(["."]) // maps as BTreeMap → deterministic key order
        // bytes fields stay as prost's default Vec<u8> — do NOT call .bytes(),
        // that opts INTO the `bytes::Bytes` type which we don't want.
        .compile_protos(&protos, &["../../proto"])
        .expect("prost-build compile");
}
