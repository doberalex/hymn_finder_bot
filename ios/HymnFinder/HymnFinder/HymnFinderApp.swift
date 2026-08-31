import SwiftUI

@main
struct HymnFinderApp: App {
    @StateObject private var library = HymnLibrary()
    @StateObject private var language = AppLanguageSettings()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(library)
                .environmentObject(language)
                .environment(\.locale, language.resolved.locale)
                .tint(Color("AccentColor"))
        }
    }
}
