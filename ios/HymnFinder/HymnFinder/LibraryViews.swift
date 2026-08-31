import SwiftUI

struct SongbooksView: View {
    @EnvironmentObject private var library: HymnLibrary
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
                    VStack(alignment: .leading, spacing: 4) {
                        Text(songbook.title).font(.headline)
                        Text("\(songbook.languageName) · \(songbook.hymnCount) песен")
                            .font(.subheadline).foregroundStyle(.secondary)
                    }.padding(.vertical, 3)
                }
            }
            .navigationTitle("Сборники")
            .searchable(text: $filter, prompt: "Название сборника")
        }
    }
}

struct SongbookDetailView: View {
    @EnvironmentObject private var library: HymnLibrary
    let songbook: Songbook
    @State private var query = ""
    @State private var results: [Hymn] = []

    var body: some View {
        List(results) { HymnRow(hymn: $0) }
            .navigationTitle(songbook.title)
            .navigationBarTitleDisplayMode(.inline)
            .searchable(text: $query, prompt: "Номер или текст")
            .task(id: query) {
                try? await Task.sleep(for: .milliseconds(180))
                guard !Task.isCancelled else { return }
                results = await library.search(query, scope: .all, songbookID: songbook.id, limit: query.isEmpty ? 5_000 : 200)
            }
    }
}

struct FavoritesView: View {
    @EnvironmentObject private var library: HymnLibrary

    var body: some View {
        NavigationStack {
            Group {
                if library.favorites.isEmpty {
                    ContentUnavailableView("Пока пусто", systemImage: "star", description: Text("Добавляйте часто используемые гимны в избранное"))
                } else {
                    List(library.favorites) { HymnRow(hymn: $0) }.listStyle(.plain)
                }
            }
            .navigationTitle("Избранное")
        }
    }
}

struct HymnDetailView: View {
    @EnvironmentObject private var library: HymnLibrary
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
                    Button("Меньше", systemImage: "textformat.size.smaller") { fontSize = max(15, fontSize - 2) }
                    Button("Больше", systemImage: "textformat.size.larger") { fontSize = min(34, fontSize + 2) }
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
    var body: some View {
        NavigationStack {
            List {
                Section("О приложении") {
                    LabeledContent("Версия", value: Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0")
                    LabeledContent("Работа без интернета", value: "Да")
                }
                Section("Подсказка") {
                    Text("Ищите по номеру, названию или нескольким словам из любого куплета. Размер текста меняется кнопкой Aa в открытом гимне.")
                }
                Section("Конфиденциальность") {
                    Text("Поисковые запросы и избранное остаются на этом устройстве. Приложение не требует регистрации.")
                }
            }.navigationTitle("Ещё")
        }
    }
}
