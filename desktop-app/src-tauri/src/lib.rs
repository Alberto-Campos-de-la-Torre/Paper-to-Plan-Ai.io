// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_opener::init())
        .setup(|_app| {
            // Spawn Python backend in a separate thread/process
            // This is a basic dev setup. For production, use Tauri Sidecar.
            std::thread::spawn(|| {
                use std::process::Command;
                // Assuming we are running from desktop-app directory or similar context
                // We use venv python and relative path. 
                // Note: In a real bundle, this path won't exist.
                let _ = Command::new("../../venv/bin/python")
                    .arg("../../backend/tauri_server.py")
                    .env("PYTHONPATH", "../../") // Add project root to PYTHONPATH
                    .status();
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
