import SwiftUI

private struct LanguageShortcut: Identifiable {
    let id: String
    let title: String
    let flag: FlagKind
}

private enum FlagKind {
    case russia, ukraine, unitedKingdom, uzbekistan
}

struct QuickAccessView: View {
    @EnvironmentObject private var library: HymnLibrary

    private let languages = [
        LanguageShortcut(id: "ru", title: "Русский", flag: .russia),
        LanguageShortcut(id: "uk", title: "Українська", flag: .ukraine),
        LanguageShortcut(id: "en", title: "English", flag: .unitedKingdom),
        LanguageShortcut(id: "uz", title: "O‘zbekcha", flag: .uzbekistan)
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                VStack(alignment: .leading, spacing: 5) {
                    Text("Быстрый доступ").font(.title2.bold())
                    Text("Откройте любимый сборник или выберите язык")
                        .font(.subheadline).foregroundStyle(.secondary)
                }

                quickSongbooks

                VStack(alignment: .leading, spacing: 12) {
                    Text("По языку").font(.headline)
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        ForEach(languages) { language in
                            NavigationLink {
                                LanguageSongbooksView(languageCode: language.id, title: language.title)
                            } label: {
                                LanguageCard(shortcut: language)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
            }
            .padding(.horizontal)
            .padding(.top, 26)
            .padding(.bottom, 28)
        }
    }

    @ViewBuilder
    private var quickSongbooks: some View {
        let books = library.quickSongbooks
        if books.isEmpty {
            Label("Закрепите сборник кнопкой булавки на его странице", systemImage: "pin")
                .font(.subheadline).foregroundStyle(.secondary)
                .frame(maxWidth: .infinity, minHeight: 72)
                .padding(.horizontal)
                .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        } else if books.count <= 2 {
            VStack(spacing: 12) {
                ForEach(books) { quickSongbook($0, compact: false) }
            }
        } else {
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                ForEach(books) { quickSongbook($0, compact: true) }
            }
        }
    }

    private func quickSongbook(_ songbook: Songbook, compact: Bool) -> some View {
        NavigationLink {
            SongbookDetailView(songbook: songbook)
        } label: {
            QuickSongbookCard(songbook: songbook, compact: compact)
        }
        .buttonStyle(.plain)
    }
}

private struct QuickSongbookCard: View {
    let songbook: Songbook
    let compact: Bool

    var body: some View {
        Group {
            if compact {
                VStack(alignment: .leading, spacing: 10) {
                    SongbookBadgeView(songbook: songbook, size: 38)
                    Spacer(minLength: 2)
                    Text(songbook.quickDisplayTitle)
                        .font(.headline).multilineTextAlignment(.leading).lineLimit(3)
                    Text("\(songbook.hymnCount) песен")
                        .font(.caption).foregroundStyle(.secondary)
                }
            } else {
                HStack(alignment: .bottom, spacing: 16) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(songbook.quickDisplayTitle).font(.headline).multilineTextAlignment(.leading)
                        Text("\(songbook.hymnCount) песен")
                            .font(.subheadline).foregroundStyle(.secondary)
                    }
                    Spacer(minLength: 8)
                    SongbookBadgeView(songbook: songbook, size: 46)
                }
            }
        }
        .frame(maxWidth: .infinity, minHeight: compact ? 126 : 78, alignment: .leading)
        .padding(compact ? 14 : 18)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(.primary.opacity(0.08), lineWidth: 1)
        }
        .contentShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

struct SongbookBadgeView: View {
    let songbook: Songbook
    let size: CGFloat

    private var symbol: String {
        let title = songbook.title.lowercased()
        if title.contains("молод") || title.contains("юност") { return "person.3.fill" }
        if title.contains("дет") { return "figure.2.and.child.holdinghands" }
        if title.contains("возрожд") || title.contains("воз.") { return "music.note.list" }
        if title.contains("неба") { return "cloud.sun.fill" }
        if title.contains("спас") { return "heart.fill" }
        if title.contains("утро") { return "sun.max.fill" }
        if title.contains("worship") || title.contains("хвал") { return "hands.clap.fill" }
        if songbook.language != "ru" { return "globe" }
        return "book.closed.fill"
    }

    var body: some View {
        Image(systemName: symbol)
            .font(.system(size: size * 0.62, weight: .semibold))
            .foregroundStyle(.primary.opacity(0.82))
            .frame(width: size, height: size)
            .accessibilityHidden(true)
    }
}

private extension Songbook {
    var quickDisplayTitle: String {
        switch title {
        case "Песнь Воз. Совета Церквей": return "Песнь Возрождения Совета Церквей"
        case "Молодежный сборник": return "Молодёжный сборник"
        default: return title
        }
    }
}

private struct LanguageCard: View {
    let shortcut: LanguageShortcut

    var body: some View {
        ZStack(alignment: .bottomLeading) {
            FlagBackdrop(kind: shortcut.flag)
            LinearGradient(colors: [.clear, .black.opacity(0.72)], startPoint: .top, endPoint: .bottom)
            HStack(alignment: .bottom) {
                Text(shortcut.title)
                    .font(.headline).foregroundStyle(.white).lineLimit(1).minimumScaleFactor(0.8)
                Spacer(minLength: 4)
                Image(systemName: "chevron.right")
                    .font(.caption.bold()).foregroundStyle(.white.opacity(0.8))
            }.padding(14)
        }
        .frame(height: 112)
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(.primary.opacity(0.08), lineWidth: 1)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(shortcut.title)
    }
}

private struct FlagBackdrop: View {
    let kind: FlagKind

    var body: some View {
        Canvas { context, size in
            let rect = CGRect(origin: .zero, size: size)
            context.fill(Path(rect), with: .color(Color(white: 0.72)))

            switch kind {
            case .russia:
                stripe(&context, rect: CGRect(x: 0, y: 0, width: size.width, height: size.height / 3), shade: 0.9)
                stripe(&context, rect: CGRect(x: 0, y: size.height / 3, width: size.width, height: size.height / 3), shade: 0.58)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 2 / 3, width: size.width, height: size.height / 3), shade: 0.32)
            case .ukraine:
                stripe(&context, rect: CGRect(x: 0, y: 0, width: size.width, height: size.height / 2), shade: 0.36)
                stripe(&context, rect: CGRect(x: 0, y: size.height / 2, width: size.width, height: size.height / 2), shade: 0.76)
            case .unitedKingdom:
                stripe(&context, rect: rect, shade: 0.28)
                diagonal(&context, size: size, from: CGPoint(x: 0, y: 0), to: CGPoint(x: size.width, y: size.height), width: 21, shade: 0.86)
                diagonal(&context, size: size, from: CGPoint(x: size.width, y: 0), to: CGPoint(x: 0, y: size.height), width: 21, shade: 0.86)
                diagonal(&context, size: size, from: CGPoint(x: 0, y: 0), to: CGPoint(x: size.width, y: size.height), width: 8, shade: 0.52)
                diagonal(&context, size: size, from: CGPoint(x: size.width, y: 0), to: CGPoint(x: 0, y: size.height), width: 8, shade: 0.52)
                stripe(&context, rect: CGRect(x: size.width * 0.39, y: 0, width: size.width * 0.22, height: size.height), shade: 0.9)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.34, width: size.width, height: size.height * 0.32), shade: 0.9)
                stripe(&context, rect: CGRect(x: size.width * 0.44, y: 0, width: size.width * 0.12, height: size.height), shade: 0.45)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.42, width: size.width, height: size.height * 0.16), shade: 0.45)
            case .uzbekistan:
                stripe(&context, rect: CGRect(x: 0, y: 0, width: size.width, height: size.height * 0.32), shade: 0.42)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.35, width: size.width, height: size.height * 0.3), shade: 0.9)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.68, width: size.width, height: size.height * 0.32), shade: 0.58)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.32, width: size.width, height: size.height * 0.03), shade: 0.18)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.65, width: size.width, height: size.height * 0.03), shade: 0.18)
                let moon = Path(ellipseIn: CGRect(x: 15, y: 13, width: 28, height: 28))
                context.fill(moon, with: .color(.white.opacity(0.9)))
                let cutout = Path(ellipseIn: CGRect(x: 22, y: 11, width: 27, height: 27))
                context.fill(cutout, with: .color(Color(white: 0.42)))
            }
        }
        .saturation(0)
    }

    private func stripe(_ context: inout GraphicsContext, rect: CGRect, shade: Double) {
        context.fill(Path(rect), with: .color(Color(white: shade)))
    }

    private func diagonal(_ context: inout GraphicsContext, size: CGSize, from: CGPoint, to: CGPoint, width: CGFloat, shade: Double) {
        var path = Path()
        path.move(to: from)
        path.addLine(to: to)
        context.stroke(path, with: .color(Color(white: shade)), lineWidth: width)
    }
}

struct LanguageSongbooksView: View {
    @EnvironmentObject private var library: HymnLibrary
    let languageCode: String
    let title: String

    private var books: [Songbook] {
        library.songbooks.filter { $0.language == languageCode }
    }

    var body: some View {
        List(books) { songbook in
            NavigationLink {
                SongbookDetailView(songbook: songbook)
            } label: {
                VStack(alignment: .leading, spacing: 4) {
                    Text(songbook.title).font(.headline)
                    Text("\(songbook.hymnCount) песен").font(.subheadline).foregroundStyle(.secondary)
                }.padding(.vertical, 4)
            }
        }
        .navigationTitle(title)
        .navigationBarTitleDisplayMode(.large)
    }
}
