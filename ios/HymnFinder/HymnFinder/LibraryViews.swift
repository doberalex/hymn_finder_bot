import SwiftUI

struct SongbooksView: View {
    @EnvironmentObject private var library: HymnLibrary
    @EnvironmentObject private var language: AppLanguageSettings
    @State private var filter = ""

    private var visibleBooks: [Songbook] {
        guard !filter.isEmpty else { return library.songbooks }
        return library.songbooks.filter { $0.title.localizedCaseInsensitiveContains(filter) }
    }

    var body: some View {
        NavigationStack {
            List(visibleBooks) { songbook in
                NavigationLink {
                    SongbookDetailView(songbook: songbook)
                } label: {
                    HStack(spacing: 12) {
                        SongbookBadgeView(songbook: songbook, size: 42)
                        VStack(alignment: .leading, spacing: 4) {
                            Text(songbook.title).font(.headline)
                            Text("\(language.languageName(songbook.language)) · \(language.format("songs_count", songbook.hymnCount))")
                                .font(.subheadline).foregroundStyle(.secondary)
                        }
                    }.padding(.vertical, 3)
                }
            }
            .navigationTitle(language.text("songbooks"))
            .searchable(text: $filter, prompt: language.text("songbook_search"))
        }
    }
}

struct SongbookDetailView: View {
    @EnvironmentObject private var library: HymnLibrary
    @EnvironmentObject private var language: AppLanguageSettings
    let songbook: Songbook
    @State private var query = ""
    @State private var results: [Hymn] = []

    var body: some View {
        List(results) { HymnRow(hymn: $0) }
            .navigationTitle(songbook.title)
            .navigationBarTitleDisplayMode(.inline)
            .searchable(text: $query, prompt: language.text("number_or_text"))
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        library.toggleQuickAccess(songbook)
                    } label: {
                        Image(systemName: library.isQuickAccess(songbook) ? "pin.fill" : "pin")
                    }
                    .accessibilityLabel(
                        library.isQuickAccess(songbook)
                        ? language.text("remove_quick")
                        : language.text("add_quick")
                    )
                }
            }
            .task(id: query) {
                try? await Task.sleep(for: .milliseconds(180))
                guard !Task.isCancelled else { return }
                results = await library.search(query, scope: .all, songbookID: songbook.id, limit: query.isEmpty ? 5_000 : 200)
            }
    }
}

struct FavoritesView: View {
    @EnvironmentObject private var library: HymnLibrary
    @EnvironmentObject private var language: AppLanguageSettings

    var body: some View {
        NavigationStack {
            Group {
                if library.favorites.isEmpty {
                    ContentUnavailableView(language.text("empty"), systemImage: "star", description: Text(language.text("favorites_hint")))
                } else {
                    List(library.favorites) { HymnRow(hymn: $0) }.listStyle(.plain)
                }
            }
            .navigationTitle(language.text("favorites"))
        }
    }
}

struct HymnDetailView: View {
    @EnvironmentObject private var library: HymnLibrary
    @EnvironmentObject private var language: AppLanguageSettings
    @AppStorage("hymnFontSize") private var fontSize = 21.0
    let hymn: Hymn

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                VStack(alignment: .leading, spacing: 7) {
                    Text("№ \(hymn.number)").font(.subheadline.weight(.semibold)).foregroundStyle(Color("AccentColor"))
                    Text(hymn.title).font(.largeTitle.bold())
                    Text(hymn.songbook).font(.subheadline).foregroundStyle(.secondary)
                    if !hymn.tune.isEmpty { Label(hymn.tune, systemImage: "music.note").font(.subheadline) }
                    if !hymn.words.isEmpty { Text(hymn.words).font(.footnote).foregroundStyle(.secondary) }
                }
                Divider()
                Text(hymn.text).font(.system(size: fontSize, design: .serif)).lineSpacing(7).textSelection(.enabled)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding()
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItemGroup(placement: .topBarTrailing) {
                Menu {
                    Button(language.text("smaller"), systemImage: "textformat.size.smaller") { fontSize = max(15, fontSize - 2) }
                    Button(language.text("larger"), systemImage: "textformat.size.larger") { fontSize = min(34, fontSize + 2) }
                } label: { Image(systemName: "textformat.size") }
                Button { library.toggleFavorite(hymn) } label: {
                    Image(systemName: library.isFavorite(hymn) ? "star.fill" : "star")
                }
                ShareLink(item: "\(hymn.number). \(hymn.title)\n\n\(hymn.text)") { Image(systemName: "square.and.arrow.up") }
            }
        }
    }
}

struct AboutView: View {
    @EnvironmentObject private var language: AppLanguageSettings

    var body: some View {
        NavigationStack {
            List {
                Section(language.text("app_language")) {
                    Picker(language.text("language"), selection: $language.selection) {
                        Text(language.systemOptionTitle).tag(AppLanguageSettings.systemValue)
                        ForEach(InterfaceLanguage.allCases) { item in
                            Text(item.nativeName).tag(item.rawValue)
                        }
                    }
                }
                Section(language.text("about")) {
                    LabeledContent(language.text("version"), value: Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0")
                    LabeledContent(language.text("offline"), value: language.text("yes"))
                }
                Section(language.text("tip")) {
                    Text(language.text("tip_text"))
                }
                Section(language.text("privacy")) {
                    Text(language.text("privacy_text"))
                }
            }.navigationTitle(language.text("more"))
        }
    }
}
