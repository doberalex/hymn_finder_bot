import SwiftUI

@main
struct HymnFinderApp: App {
    @StateObject private var library = HymnLibrary()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(library)
                .tint(Color("AccentColor"))
        }
    }
}
