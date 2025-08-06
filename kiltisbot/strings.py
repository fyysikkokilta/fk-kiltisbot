"""
This file contains all longer messages that bot sends.
"""

INSTRUCTIONS_MSG = """Jos haluat lisätietoja sähköisen kiltispikkin käytöstä kirjoita /piikki_ohje.

@Fk_kiltisbot on suora yhteys kiltistoimikuntaan ja se on tarkoitettu palautteen ja kehitysehdotusten välittämiseen \
tai maidon yms. puutteesta valittamiseen.

Viestittely botin kanssa toimii siten, että lähetät tälle botille viestin. Yksityisviestit ovat automaattisesti \
anonyymejä \
ja tuetut viestimuodot ovat ainakin teksti, kuva, video, stikkeri, ympyrävideo, gifi, tiedosto, sijainti ja ääni. \
Botti mahdollistaa, että kiltistoimarit myös vastata botin kautta viesteihisi. \
Jos haluat, että kiltistoimikunta tietää kuka olet, allekirjoita viestisi.

Botti tallentaa lähettämistäsi viesteistä sinun ja botin kahdenkeskisen keskustelun id:n ja lähetetyn viestin id:n \
välimuistissa olevaan tietorakenteeseen. Epärehellinen ylläpitäjä voisi periaatteessa identiteettisi sieltä onkia. \
Minun kiinnostukseni ei ainakaan tähän riitä ja lisäksi olen rehellinen, joten henkilöllisyytesi on turvassa.

Kiltisbot osaa myös hakea killan tulevat tapahtumat Google-kalenterista, jos kirjoitat /tapahtumat.

Viikkotiedotteet saat komennoilla /viikkotiedote (suomeksi) tai /weekly (englanniksi).

Vikatilanteissa ja kehitysehdotuksissa ota yhteyttä @elias_yj.

Muista myös kiltistoimikunnan muut palvelut kuten @TsufeBot.

Kiltisbotin lähdekoodi: https://github.com/fyysikkokilta/fk-kiltisbot"""


INSTRUCTIONS_IN_ENGLISH_MSG = """To know more about Guild's candy store write /candy_store.

@Fk_kiltisbot is a direct communication channel to maintainers of the Guild room. Any feedback is appreciated whether \
is improvement suggestion or just notice that coffee has run out!

<b>Messages to Guild room committee</b>

You can contact Guild room committee by simply sending message to the bot. All messages will be answered. All \
relevant message types that Telegram supports are supported. Message will be anonymous unless you manually sign \
your message (in principle your telegram user id is saved to log files which could be used to figure out your \
identity but that is not something we would bother to do).

<b>Weekly newsletters</b>

Get the latest weekly newsletter with /weekly command.

See also: @TsufeBot
Source code: https://github.com/fyysikkokilta/fk-kiltisbot """


START_MSG = """Hello!😊

Kirjoita /help, niin pääset alkuun.

To get started press /help_in_english"""


HELP_MSG = """For information in English, press /help_in_english

Tämä on kiltistoimikunnan botti, jonka tarkoituksena on parantaa kiltalaisten kiltiskokemusta.

Jos haluat lisätietoja kiltistoimikunnan kanssa viestittelystä kirjoita:
/viesti_ohje

Jos haluat lisätietoja sähköisestä piikistä, kirjoita:
/piikki_ohje

Viikkotiedotteet:
/viikkotiedote - Suomenkielinen viikkotiedote
/weekly - Weekly newsletter in English"""


HELP_IN_ENGLISH_MSG = """This bot is maintained by Guild room committee of the Guild of physics. It provides various \
Telegram integrations of Guild's services e.g. calendars and candy store.

How to communicate with Guild room committee via this bot:
/messaging_instructions

More info about candy store:
/candy_store

Weekly newsletters:
/viikkotiedote - Suomenkielinen viikkotiedote
/weekly - Weekly newsletter in English

We encourage to experiment with other commands as well."""


TAB_INSTRUCTIONS_MSG = """<b>Sähköinen kiltispiikki</b>

Tämä on kiltiksen sähköinen piikkijärjestelmä. Fyysisesti raha ja herkut liikkuvat kuin aina ennekin, \
mutta tällä botilla on tarkoitus:
- poistaa turha sekalaisen paperinipun pläräily
- vähentää ikäviä desimaalilukujen päässälaskuja
- säästää kiltisvastaavat uusien listojen kirjoittamisen vaivalta
- kerätä kulutusdataa kiltiksen palveluiden parantamiseksi.

Vikatilanteissa ja kehitysehdotuksissa ota yhteyttä @Stippos tai voit ottaa yhteyttä myös suoraan tällä botilla, \
mistä saat listätietoa kirjoittamalla /viesti_ohje.

Sähköisellä kiltispiikillä voi tällä hetkellä tehdä seuraavia asioita:

/kirjaudu
Ennen botin käytön aloittamista sinun tulee rekisteröityä tällä komennolla.

/saldo
Täältä voit tarkistaa tai muuttaa saldoasi. Komento hyväksyy positiiviset desimaaliluvut. \
Fyysisesti rahan lisääminen toimii kuten aina ennenkin.

/kauppa
Täällä voit tehdä ostoksia. Kun painat näytöllä olevaa tuotenappulaa, \
vähennetään sen hinta automaattisesti sinun saldostasi.

/hinnasto
Täällä voit tarkastella tarjontaa myös listamuodossa.

/poista_edellinen
Jos sinulle käy virhe käyttäessäsi bottia, voit peruuttaa edellisen toimintosi tällä komennolla. \
Komento toimii ostosten lisäksi myös saldon muutoksiin. Voit toistaa tapahtuman tarvittaessa useaan \
kertaan ja iteroida virheitäsi taaksepäin niin pitkään kuin on tarvis."""


TAB_INSTRUCTIONS_IN_ENGLISH_MSG = """<b>Digital candy store</b>

Purpose of this system is to make the use of the candy closet ("herkkukaappi" in Finnish) in the Guild room easier \
by replacing old balance sheet paper with an electronic system. \
In addition it provides accurate consumption data for the Guild room committee \
to improve assortment of the candy closet. System has following commands:

/kirjaudu
Register as a bot user before starting to use it.

/saldo
Inspect or change your balance. Command accepts all positive decimal numbers. \
Physically you should add money to a jar in the candy closet.

/kauppa
Here you can buy goodies. When you press product in the screen its price is automatically reduced from your balance.

/hinnasto
Prints a list of all products and their prices.

/poista_edellinen
Undo previous transaction that changed your balance. These actions can be chained as many times as needed."""


TERMS_OF_USE_MSG = """<b>Käyttöehdot / Terms of use</b>

Tämä on sähköinen kiltispiikki, johon voit kirjata piikistä ostamasi tuotteet sekä sinne lisäämäsi rahat. \
Piikin käyttämistä varten sinusta tallennetaan nimesi sekä Telegramin käyttäjätunnuksesi.

Myös tekemäsi ostokset tallennetaan, jotta ne on vahingon sattuessa myös mahdollista peruuttaa kätevästi. \
Tapahtumiin ei liitetä ostajan nimeä, joten datasta ei esimerkiksi suoraan näe, \
että kylläpäs Jonne juo paljon Power Kingiä. \
Sen päätteleminen on kuitenkin periaatteessa mahdollista. \
Ostoksista kertyvää dataa on tarkoitus käyttää kiltiksen valikoiman kehittämiseen.

Onko tämä fine?


***

This bot provides you an interface to use Guild room's candy store by marking here your purchases and money that you \
add to the candy store slate. In order to use these features we save your Telegram display name and username.

Each individual purchase is saved to make possible to undo each transaction. Your name is not attached directly to \
each transaction so maintainers of this bot can not see directly what you buy. Deducing this is possible in principle. \
However data is only used to improve store's availability and assortment.

Are you ok with this?"""
