import { BookOpenText, Languages, Mail, MessageCircle, Search, ShieldCheck, Star } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';

const features = [
  { icon: Search, title: 'Быстрый поиск', text: 'По номеру, названию или любой строке из текста гимна.' },
  { icon: BookOpenText, title: '16 542 гимна', text: 'Сборники доступны полностью офлайн — интернет не требуется.' },
  { icon: Languages, title: 'Четыре языка', text: 'Русский, украинский, английский и узбекский каталоги.' },
  { icon: Star, title: 'Всё под рукой', text: 'Избранные гимны и настраиваемый быстрый доступ к сборникам.' },
];

const faqs = [
  ['Нужен ли интернет?', 'Нет. Каталог загружается вместе с приложением, поиск и чтение работают офлайн.'],
  ['Как изменить язык интерфейса?', 'Откройте «Ещё» → «Язык приложения». Тексты гимнов при этом не переводятся.'],
  ['Как добавить сборник в быстрый доступ?', 'Откройте сборник и нажмите значок булавки в правом верхнем углу.'],
  ['Как сообщить об ошибке в тексте?', 'Напишите нам по email или в Telegram. Укажите сборник, номер гимна и правильный вариант.'],
];

export default function Home() {
  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Гимны — начало страницы"><Image src="/app-icon.png" width={36} height={36} alt="" /><span>Гимны</span></a>
        <nav aria-label="Основная навигация"><a href="#help">Помощь</a><a href="#contact">Контакты</a><Link href="/privacy">Конфиденциальность</Link></nav>
      </header>

      <section id="top" className="hero">
        <div>
          <p className="eyebrow">Поддержка приложения</p>
          <h1>Гимны всегда рядом</h1>
          <p className="lead">Офлайн-каталог христианских гимнов с быстрым поиском по номеру, названию и тексту.</p>
          <div className="hero-actions"><a className="button primary" href="#help">Найти ответ</a><a className="button secondary" href="#contact">Связаться с нами</a></div>
        </div>
        <Image className="hero-icon" src="/app-icon.png" width={280} height={280} priority alt="Иконка приложения «Гимны»" />
      </section>

      <section className="feature-grid" aria-label="Возможности приложения">
        {features.map(({ icon: Icon, title, text }) => <article className="feature-card" key={title}><Icon aria-hidden="true" /><h2>{title}</h2><p>{text}</p></article>)}
      </section>

      <section id="help" className="content-section">
        <div className="section-heading"><p className="eyebrow">Частые вопросы</p><h2>Как мы можем помочь?</h2></div>
        <div className="faq-list">{faqs.map(([question, answer]) => <details key={question}><summary>{question}</summary><p>{answer}</p></details>)}</div>
      </section>

      <section id="contact" className="contact-card">
        <div><p className="eyebrow">Обратная связь</p><h2>Расскажите, что можно улучшить</h2><p>Для быстрого ответа приложите модель iPhone, версию iOS и снимок экрана.</p></div>
        <div className="contact-links">
          <a href="mailto:teleginalex2905@gmail.com"><Mail aria-hidden="true" />teleginalex2905@gmail.com</a>
          <a href="https://t.me/doberalex" target="_blank" rel="noreferrer"><MessageCircle aria-hidden="true" />Telegram @doberalex</a>
        </div>
      </section>

      <footer><div className="brand"><Image src="/app-icon.png" width={36} height={36} alt="" /><span>Гимны</span></div><p><ShieldCheck aria-hidden="true" /> Приложение не собирает персональные данные.</p><Link href="/privacy">Политика конфиденциальности</Link></footer>
    </main>
  );
}
