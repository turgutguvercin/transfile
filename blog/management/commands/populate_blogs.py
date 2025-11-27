from io import BytesIO
from typing import Dict, List, Optional

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import translation
from django.utils.text import slugify
from PIL import Image

from blog.models import Blog


class Command(BaseCommand):
    help = 'Populate Blog with multilingual AI-translation articles. Use --reset to wipe first.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing Blog entries before populating.'
        )

    def handle(self, *args, **options):
        reset: bool = options.get('reset', False)

        if reset:
            deleted_count, _ = Blog.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted all blogs (rows affected: {deleted_count}).'))

        # Articles grouped by a topic key so all language variants map to one Blog
        articles: List[Dict] = [
            {
                'topic': 'future-of-ai-translation',
                'translations': [
                    {
                        'language_code': 'en',
                        'title': 'AI Translation: The Future of Language Processing',
                        'content': 'AI translation is revolutionizing the way we understand and communicate across languages. With advancements in neural networks and machine learning, AI translation tools are becoming more accurate and efficient. These tools are not only breaking down language barriers but also enabling real-time communication across different cultures. The future of AI translation looks promising as it continues to evolve and integrate with other technologies, making global communication seamless and more accessible than ever before.'
                    },
                    {
                        'language_code': 'es',
                        'title': 'Traducción AI: El futuro del procesamiento del lenguaje',
                        'content': 'La traducción AI está revolucionando la forma en que entendemos y comunicamos a través de los idiomas. Con los avances en redes neuronales y aprendizaje automático, las herramientas de traducción AI se están volviendo más precisas y eficientes. Estas herramientas no solo están rompiendo las barreras del idioma, sino que también están permitiendo la comunicación en tiempo real entre diferentes culturas. El futuro de la traducción AI parece prometedor a medida que continúa evolucionando e integrándose con otras tecnologías, haciendo que la comunicación global sea más fluida y accesible que nunca.'
                    },
                    {
                        'language_code': 'fr',
                        'title': "Traduction AI : L'avenir du traitement du langage",
                        'content': "La traduction AI révolutionne la façon dont nous comprenons et communiquons à travers les langues. Avec les avancées des réseaux neuronaux et de l'apprentissage automatique, les outils de traduction AI deviennent de plus en plus précis et efficaces. Ces outils ne se contentent pas de briser les barrières linguistiques, ils permettent également une communication en temps réel entre différentes cultures. L'avenir de la traduction AI semble prometteur alors qu'elle continue d'évoluer et de s'intégrer à d'autres technologies, rendant la communication mondiale plus fluide et accessible que jamais."
                    },
                    {
                        'language_code': 'de',
                        'title': 'AI Übersetzung: Die Zukunft der Sprachverarbeitung',
                        'content': 'Die AI-Übersetzung revolutioniert die Art und Weise, wie wir Sprachen verstehen und kommunizieren. Mit Fortschritten in neuronalen Netzwerken und maschinellem Lernen werden AI-Übersetzungstools immer genauer und effizienter. Diese Tools überwinden nicht nur Sprachbarrieren, sondern ermöglichen auch die Echtzeitkommunikation zwischen verschiedenen Kulturen. Die Zukunft der AI-Übersetzung sieht vielversprechend aus, da sie sich weiterentwickelt und in andere Technologien integriert, wodurch die globale Kommunikation nahtloser und zugänglicher wird als je zuvor.'
                    },
                    {
                        'language_code': 'tr',
                        'title': 'AI Çeviri: Dil İşlemenin Geleceği',
                        'content': 'AI çeviri, dilleri anlama ve iletişim kurma şeklimizi devrim niteliğinde değiştiriyor. Sinir ağları ve makine öğrenimindeki gelişmelerle, AI çeviri araçları daha doğru ve verimli hale geliyor. Bu araçlar sadece dil engellerini aşmakla kalmıyor, aynı zamanda farklı kültürler arasında gerçek zamanlı iletişimi de mümkün kılıyor. AI çevirinin geleceği, diğer teknolojilerle entegre olmaya devam ettikçe umut verici görünüyor ve küresel iletişimi her zamankinden daha sorunsuz ve erişilebilir hale getiriyor. AI çeviri, iş dünyasından eğitime, sağlık hizmetlerinden turizme kadar birçok sektörde devrim yaratıyor. Özellikle, AI çeviri araçları, uluslararası iş toplantılarında ve konferanslarda dil engellerini ortadan kaldırarak, katılımcıların daha etkili bir şekilde iletişim kurmasını sağlıyor. Eğitim alanında, AI çeviri, öğrencilerin farklı dillerdeki kaynaklara erişimini kolaylaştırarak, öğrenme sürecini zenginleştiriyor. Sağlık hizmetlerinde, AI çeviri, doktorlar ve hastalar arasında dil engellerini ortadan kaldırarak, daha iyi bir hasta bakımı sağlıyor. Turizm sektöründe ise, AI çeviri, turistlerin yerel halkla daha iyi iletişim kurmasını sağlayarak, seyahat deneyimlerini geliştiriyor.'
                    },
                ]
            },
            {
                'topic': 'ai-impact-global-communication',
                'translations': [
                    {
                        'language_code': 'en',
                        'title': 'The Impact of AI on Global Communication',
                        'content': 'Artificial Intelligence is transforming global communication by providing tools that can translate languages in real-time. This technology is not only bridging the gap between different cultures but also enhancing business operations by enabling seamless communication across borders. As AI continues to evolve, it is expected to play a crucial role in international diplomacy, education, and tourism, making the world more connected than ever before.'
                    },
                    {
                        'language_code': 'tr',
                        'title': 'AI ve Küresel İletişim Üzerindeki Etkisi',
                        'content': 'Yapay Zeka, dilleri gerçek zamanlı olarak çevirebilen araçlar sağlayarak küresel iletişimi dönüştürüyor. Bu teknoloji, farklı kültürler arasındaki boşluğu kapatmakla kalmıyor, aynı zamanda sınır ötesi kesintisiz iletişimi mümkün kılarak iş operasyonlarını da geliştiriyor. AI gelişmeye devam ettikçe, uluslararası diplomasi, eğitim ve turizmde önemli bir rol oynaması bekleniyor ve dünyayı her zamankinden daha fazla birbirine bağlı hale getiriyor.'
                    },
                    {
                        'language_code': 'fr',
                        'title': 'L’impact de l’IA sur la communication mondiale',
                        'content': 'L’intelligence artificielle transforme la communication mondiale en fournissant des outils capables de traduire les langues en temps réel. Cette technologie ne se contente pas de combler le fossé entre différentes cultures, elle améliore également les opérations commerciales en permettant une communication fluide au-delà des frontières. À mesure que l’IA continue d’évoluer, elle devrait jouer un rôle crucial dans la diplomatie internationale, l’éducation et le tourisme, rendant le monde plus connecté que jamais.'
                    },
                    {
                        'language_code': 'es',
                        'title': 'El impacto de la IA en la comunicación global',
                        'content': 'La inteligencia artificial está transformando la comunicación global al proporcionar herramientas que pueden traducir idiomas en tiempo real. Esta tecnología no solo está cerrando la brecha entre diferentes culturas, sino que también está mejorando las operaciones comerciales al permitir una comunicación fluida a través de las fronteras. A medida que la IA continúa evolucionando, se espera que desempeñe un papel crucial en la diplomacia internacional, la educación y el turismo, haciendo que el mundo esté más conectado que nunca.'
                    },
                ]
            },
            {
                'topic': 'pipeline-ocr-llm-qa',
                'translations': [
                    {
                        'language_code': 'en',
                        'title': 'Building an AI Translation Pipeline: From OCR to LLM QA',
                        'content': 'Designing a production-grade AI translation pipeline requires orchestrating multiple components: document ingestion, OCR, sentence segmentation, translation, quality assurance, and delivery. High-quality OCR is essential for PDFs and scans; without reliable text extraction, downstream translation quality suffers. Next, robust sentence segmentation and language detection help avoid mistranslations. NMT or LLM translators can be combined with domain glossaries and style guides to enforce consistent terminology. Automated QA—grammar checks, terminology validation, and back-translation sampling—catches errors at scale. Observability enables continuous optimization.'
                    },
                ]
            },
            {
                'topic': 'term-management-llm',
                'translations': [
                    {
                        'language_code': 'tr',
                        'title': 'LLM Destekli Çeviride Terim Yönetimi ve Sözlük Entegrasyonu',
                        'content': 'Kurumsal ölçekte AI çeviri uygulamalarında en büyük zorluklardan biri terim tutarlılığını korumaktır. LLM modelleri güçlü bir akıcılık sunarken, marka terminolojisi veya teknik sözcüklerde hataya düşebilir. Bunun önüne geçmek için kapsamlı bir terim listesi ve stil kılavuzu oluşturulmalı, motorlara öncelikli ipuçları veya kurallar olarak beslenmelidir. Çeviri sonrası otomatik terim doğrulama ve QA adımları süreçte kritik rol oynar.'
                    },
                ]
            },
            {
                'topic': 'quality-metrics',
                'translations': [
                    {
                        'language_code': 'fr',
                        'title': 'Qualité en traduction IA : mesures, tests et amélioration continue',
                        'content': 'Assurer la qualité en traduction IA requiert des métriques automatiques (BLEU, COMET, chrF) combinées à des évaluations humaines. Des tests A/B, l’analyse d’erreurs et le suivi des régressions permettent d’orienter les améliorations. La mise en place de boucles de feedback (post-editing) et de mémoires de traduction soutient la personnalisation du système.'
                    },
                ]
            },
            {
                'topic': 'compliance-privacy',
                'translations': [
                    {
                        'language_code': 'es',
                        'title': 'Privacidad y cumplimiento en traducción con IA',
                        'content': 'El cumplimiento (GDPR, HIPAA, SOC 2) es esencial al manejar documentos sensibles. La arquitectura segura incluye cifrado en tránsito y en reposo, anonimización de datos y políticas de retención claras. Flujos sin registro con proveedores y auditorías internas reducen el riesgo de exposición.'
                    },
                ]
            },
            {
                'topic': 'cost-optimization',
                'translations': [
                    {
                        'language_code': 'de',
                        'title': 'Kostenoptimierung bei KI-Übersetzung: Routing und Caching',
                        'content': 'Bei großen Volumina steigen Kosten und Latenzen schnell. Dynamisches Routing sendet Alltagsinhalte zu günstigeren NMT-Providern, während hochsichtbare Inhalte einen Premium-LLM-Pfad nutzen. Mehrstufiges Caching reduziert Wiederholungen, KPIs machen Optimierung messbar.'
                    },
                ]
            },
            {
                'topic': 'strategy-nmt-vs-rules',
                'translations': [
                    {
                        'language_code': 'ru',
                        'title': 'НМТ против правил: как выбрать стратегию перевода',
                        'content': 'НМТ обеспечивает высокую беглость, но может ошибаться в терминологии. Правиловые системы предсказуемы, но ограничены по стилю и охвату языков. Гибридный пайплайн с нормализацией текста, глоссариями и автоматическим QA снижает риски без потери скорости.'
                    },
                ]
            },
            {
                'topic': 'glossary-style-guide',
                'translations': [
                    {
                        'language_code': 'ja',
                        'title': '用語集とスタイルガイドの統合によるLLM翻訳の安定化',
                        'content': '企業向け翻訳では、用語の一貫性と文体の統一が不可欠。システムプロンプトでガードレールを設定し、用語集とスタイルガイドを明示的に渡すことで出力のばらつきを抑制。翻訳後は自動QAで逸脱を検出。'
                    },
                ]
            },
            {
                'topic': 'seo-localization',
                'translations': [
                    {
                        'language_code': 'it',
                        'title': 'SEO multilingue e localizzazione dei contenuti con l’IA',
                        'content': 'Per la visibilità internazionale, la localizzazione SEO richiede ricerca per paese, riscrittura dei meta tag e adattamento culturale. L’IA suggerisce varianti naturali, mentre il controllo umano garantisce coerenza del brand.'
                    },
                ]
            },
            {
                'topic': 'rtl-languages',
                'translations': [
                    {
                        'language_code': 'ar',
                        'title': 'التعامل مع اللغات من اليمين إلى اليسار في أنظمة الترجمة بالذكاء الاصطناعي',
                        'content': 'تتطلب اللغات من اليمين إلى اليسار اهتماماً خاصاً في العرض وتقسيم الجمل والرموز المختلطة. يجب ضبط اتجاه النص واستخدام خطوط متوافقة لضمان قابلية القراءة. اكتشاف النص ثنائي الاتجاه وتطبيع علامات الترقيم يمنع الأخطاء.'
                    },
                ]
            },
            {
                'topic': 'enterprise-reliability',
                'translations': [
                    {
                        'language_code': 'zh-hans',
                        'title': '企业级AI翻译：可靠性、观测性与SLA',
                        'content': '企业级AI翻译需要高可靠性与可观测性。建议采用队列驱动的任务架构、幂等重试与速率限制。观测指标（延迟、成本、后编辑工作量等）支持持续优化与SLA承诺。'
                    },
                ]
            },
        ]

        def generate_placeholder_image(language_code: str, width: int = 1200, height: int = 800) -> ContentFile:
            palette = {
                'en': (79, 70, 229),
                'tr': (220, 38, 38),
                'fr': (59, 130, 246),
                'es': (245, 158, 11),
                'de': (16, 185, 129),
                'ru': (99, 102, 241),
                'ja': (236, 72, 153),
                'it': (34, 197, 94),
                'ar': (15, 118, 110),
                'zh-hans': (234, 88, 12),
            }
            color = palette.get((language_code or '').lower(), (120, 120, 120))
            img = Image.new('RGB', (width, height), color)
            buf = BytesIO()
            img.save(buf, format='PNG', optimize=True)
            buf.seek(0)
            return ContentFile(buf.getvalue())

        def likely_mismatch(lang: str, text: str) -> bool:
            if not text:
                return False
            has_arabic = any('\u0600' <= ch <= '\u06FF' for ch in text)
            has_cyrillic = any('\u0400' <= ch <= '\u04FF' for ch in text)
            has_hiragana = any('\u3040' <= ch <= '\u309F' for ch in text)
            has_katakana = any('\u30A0' <= ch <= '\u30FF' for ch in text)
            has_cjk = any('\u4E00' <= ch <= '\u9FFF' for ch in text)

            if lang == 'ar':
                return not has_arabic
            if lang == 'ru':
                return not has_cyrillic
            if lang == 'ja':
                return not (has_hiragana or has_katakana)
            if lang == 'zh-hans':
                return not has_cjk
            if lang in {'en', 'tr', 'fr', 'es', 'de', 'it'}:
                return has_arabic or has_cyrillic or has_hiragana or has_katakana or has_cjk
            return False

        def find_existing_blog_by_translations(translations_data: List[Dict]) -> Optional[Blog]:
            for tr in translations_data:
                lang = tr['language_code']
                title = tr['title']
                existing = Blog.objects.filter(
                    translations__language_code=lang,
                    translations__title=title
                ).first()
                if existing:
                    return existing
            return None

        # Upsert: one Blog per topic with multiple language translations
        for article in articles:
            topic = article['topic']
            translations_data = article['translations']

            blog = find_existing_blog_by_translations(translations_data)

            # Create base blog using the first translation if not found
            if blog is None:
                primary = translations_data[0]
                # Activate correct language so model save generates per-language slug correctly
                translation.activate(primary['language_code'])
                blog = Blog()
                blog.set_current_language(primary['language_code'])
                blog.title = primary['title']
                blog.content = primary['content']
                blog.seo_title = primary['title']
                blog.seo_explanation = primary['content'][:160]
                blog.save()

                # Attach placeholder image (converted to WEBP by model.save)
                placeholder = generate_placeholder_image(primary['language_code'])
                image_name = f"{slugify(primary['title'])}.png"
                blog.image.save(image_name, placeholder, save=False)
                blog.save()
                self.stdout.write(self.style.SUCCESS(f"Created blog for topic: {topic} [{primary['language_code']}]"))

            # Ensure/update all translations for this blog
            for tr in translations_data:
                lang = tr['language_code']
                if likely_mismatch(lang, tr['content']):
                    self.stdout.write(self.style.WARNING(
                        f"Language/content mismatch suspected for [{lang}] '{tr['title'][:50]}...'"
                    ))
                # Activate current language before saving, so slugs and fields persist to that locale
                translation.activate(lang)
                blog.set_current_language(lang)
                blog.title = tr['title']
                blog.content = tr['content']
                blog.seo_title = tr['title']
                blog.seo_explanation = tr['content'][:160]
                blog.save()
                self.stdout.write(self.style.SUCCESS(f"Upserted translation: {tr['title']} [{lang}]"))

        translation.deactivate()
        self.stdout.write(self.style.SUCCESS('Populate completed.'))

