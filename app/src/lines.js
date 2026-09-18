// Maps a save-file puzzle path to the narration line that should play once its
// trigger flag (HasBeenOpened or HasBeenSolved) becomes true.
//
// verified: true  -> path confirmed against real/checkpoint save data.
// verified: false -> path not found in any known save; constructed from the same
//   zero-padding convention as verified sibling puzzles in that folder. Re-confirm
//   once real play reaches that region.
module.exports = {
  'AGeri/Puzzles/Data/Tutorial-1': {
    id: 'N01',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Welcome to Glimmith, Artisan. I am Elias, keeper of the window designs. We used to have a much longer introduction, but most visitors stopped listening before we reached the bridge.',
    textKo:
      '글리미스에 오신 것을 환영합니다, 장인. 저는 창의 도안을 관리하는 엘리아스입니다. 예전에는 인사말이 훨씬 길었는데, 다리에 도착하기도 전에 방문객들이 듣기를 포기하더군요.',
    voiceFile: 'N01.mp3',
  },
  'AGeri/Puzzles/Zone1/1-single-shape/0049.puz': {
    id: 'N02',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Start with whichever window catches your eye. The shapes need care. The colours are your decision. I once spent six weeks settling an argument about green, and I would rather not do it again.',
    textKo:
      '마음이 가는 창부터 시작하십시오. 형태는 잘 맞춰야 하지만, 색은 그대가 정하면 됩니다. 초록색을 두고 벌어진 다툼을 중재하느라 육 주를 쓴 적이 있는데, 다시 하고 싶지는 않군요.',
    voiceFile: 'N02.mp3',
  },
  'AGeri/Puzzles/Zone1/1-single-shape/0643.puz': {
    id: 'N03',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'You may wonder why so much glass remains when so little else does. It broke easily enough. I can assure you of that. Getting rid of what it held was another matter.',
    textKo:
      '다른 것은 거의 남지 않았는데 왜 유리만 이렇게 많은지 궁금할지도 모르겠습니다. 깨뜨리기 쉬운 유리였다는 것만은 제가 보장하지요. 다만 그 안에 남은 것까지 없애기는 어려웠습니다.',
    voiceFile: 'N03.mp3',
  },
  'AGeri/Puzzles/Zone1/2-shape-bank/0051.puz': {
    id: 'N04',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'People came up here at sunset with supper wrapped in cloth. They stayed until the lamps came on below, usually claiming they were about to leave whenever someone asked.',
    textKo:
      '사람들은 천에 저녁거리를 싸 들고 해질녘 이곳에 올라왔습니다. 아래쪽에 등불이 켜질 때까지 머물면서도, 누가 물으면 늘 이제 막 내려가려던 참이라고 했지요.',
    voiceFile: 'N04.mp3',
  },
  'AGeri/Puzzles/Zone1/2-shape-bank/0059.puz': {
    id: 'N05',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Mara had a favourite bench here. Visitors kept asking her for directions, so she began giving them, including directions to places she had never visited. She sounded very sure of herself.',
    textKo:
      '마라에게는 이곳에 즐겨 앉는 벤치가 있었습니다. 방문객들이 자꾸 길을 묻자, 가 보지도 않은 곳까지 안내하기 시작했지요. 말투만큼은 아주 확신에 차 있었습니다.',
    voiceFile: 'N05.mp3',
  },
  'AGeri/Puzzles/Zone1/2-shape-bank/0052.puz': {
    id: 'N06',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Mara—that was her name. I had the bench, the red scarf, even the laugh, but not the name until just now. She would have enjoyed making me ask twice.',
    textKo:
      '마라. 그 이름이었군요. 벤치도, 붉은 목도리도, 웃음소리도 떠올랐는데 이름은 이제야 생각났습니다. 두 번이나 이름을 물었다면 아주 신나게 저를 놀렸을 겁니다.',
    voiceFile: 'N06.mp3',
  },
  'AGeri/Puzzles/Zone1/4-slash-pack/0210.puz': {
    id: 'N07',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Rose windows were popular for weddings, births, and new shops. One family ordered a small one when their son finally moved out. They told him it was for his birthday.',
    textKo:
      '장미창은 결혼이나 출산, 새 가게의 개업을 기념할 때 인기였습니다. 아들이 드디어 분가하자 작은 창을 주문한 가족도 있었지요. 아들에게는 생일 기념이라고 했습니다.',
    voiceFile: 'N07.mp3',
  },
  'AGeri/Puzzles/Zone1/4-slash-pack/0211.puz': {
    id: 'N08',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'A baker ordered twelve shades of amber for her thousandth loaf. We talked her down to five, though she counted them every time she visited. I handled the invoice myself.',
    textKo:
      '어느 제빵사는 천 번째 빵을 판 기념으로 열두 가지 호박색을 주문했습니다. 다섯 가지로 줄이기는 했지만, 방문할 때마다 색을 세어 보더군요. 청구서는 제가 직접 처리했습니다.',
    voiceFile: 'N08.mp3',
  },
  'AGeri/Puzzles/Zone1/4-slash-pack/1284pad.puz': {
    id: 'N09',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Years later, that shop stood empty, but people still smelled warm bread when sunlight crossed the window. I went to check the ovens. They were cold.',
    textKo:
      '몇 년 뒤 그 가게가 비어 버린 후에도, 창으로 햇빛이 들면 따뜻한 빵 냄새가 난다는 사람들이 있었습니다. 저는 화덕을 확인하러 갔습니다. 차갑더군요.',
    voiceFile: 'N09.mp3',
  },
  'AGeri/Puzzles/Zone1/3-gemini-delta/0095.puz': {
    id: 'N10',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Two sisters shared this workshop. Customers often paid the wrong sister, which was harmless until the sisters began charging different prices. After that, I received a great many letters.',
    textKo:
      '자매 두 명이 이 작업실을 함께 썼습니다. 손님들이 엉뚱한 자매에게 돈을 주곤 했는데, 두 사람이 서로 다른 값을 받기 시작하면서 문제가 됐지요. 그 뒤로 제게 편지가 아주 많이 왔습니다.',
    voiceFile: 'N10.mp3',
  },
  'AGeri/Puzzles/Zone1/3-gemini-delta/1271.puz': {
    id: 'N11',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'One sister loved repeating patterns. The other refused to repeat anything. They shared a workshop for thirty-seven years and disagreed about every window. Neither ever asked to move.',
    textKo:
      '한 사람은 반복되는 무늬를 좋아했고, 다른 한 사람은 무엇이든 반복하기를 싫어했습니다. 삼십칠 년 동안 같은 작업실을 쓰며 모든 창을 두고 다퉜지요. 나가겠다는 사람은 없었습니다.',
    voiceFile: 'N11.mp3',
  },
  'AGeri/Puzzles/Zone1/3-gemini-delta/0693b.puz': {
    id: 'N12',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'One morning, each sister remembered making the other\'s half of a window. They came to me expecting an argument over the bill. Both described the same small cut on the same finger.',
    textKo:
      '어느 날 아침, 자매는 서로 상대방 몫의 창을 자신이 만들었다고 기억했습니다. 대금을 두고 다투러 제게 찾아왔지요. 두 사람 모두 같은 손가락에 났던 똑같은 작은 상처를 설명했습니다.',
    voiceFile: 'N12.mp3',
  },
  'AGeri/Puzzles/Zone1/5-shape-bank/0238.puz': {
    id: 'N13',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Every apprentice started with shapes. Before anyone trusted them with an expensive colour, they had to make a corner meet another corner. This caused more resentment than you might expect.',
    textKo:
      '견습생은 누구나 모양부터 배웠습니다. 비싼 색유리를 맡기기 전에 모서리와 모서리부터 제대로 맞춰야 했지요. 예상보다 훨씬 많은 원망을 사는 과정이었습니다.',
    voiceFile: 'N13.mp3',
  },
  'AGeri/Puzzles/Zone1/5-shape-bank/0239.puz': {
    id: 'N14',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The apprentices complained that the old masters cared more about rules than people. We had said exactly the same thing at their age. Some of us had used the same words.',
    textKo:
      '견습생들은 늙은 대가들이 사람보다 규칙을 더 아낀다고 불평했습니다. 우리도 그 나이 때 똑같은 말을 했지요. 토씨까지 같은 경우도 있었습니다.',
    voiceFile: 'N14.mp3',
  },
  'AGeri/Puzzles/Zone1/5-shape-bank/0266.puz': {
    id: 'N15',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'An apprentice once changed a shape in a window that held a lullaby. It still looked lovely, but the tune came back wrong. His mother noticed before any of the masters did.',
    textKo:
      '한 견습생이 자장가를 담은 창의 모양을 조금 바꾼 적이 있습니다. 보기에는 여전히 아름다웠는데, 흘러나오는 곡조가 달라졌지요. 대가들보다 먼저 알아챈 사람은 그 아이의 어머니였습니다.',
    voiceFile: 'N15.mp3',
  },
  'AGeri/Puzzles/Zone1/9-region-size-x/0070.puz': {
    id: 'N16',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Changing the colour never altered that lullaby. Changing the shape did, even when we could barely see the difference. That is why I fuss over your corners, Artisan.',
    textKo:
      '색을 바꿔도 그 자장가는 달라지지 않았습니다. 하지만 모양을 바꾸면, 눈에 거의 차이가 없어도 곡조가 달라졌지요. 제가 그대의 모서리를 그토록 따지는 이유입니다, 장인.',
    voiceFile: 'N16.mp3',
  },
  'AGeri/Puzzles/Zone1/9-region-size-x/0244.puz': {
    id: 'N17',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Our first memory-glass held a tune or a face. Later, we could preserve a whole room, right down to the rain against its roof. People queued for hours to hear it.',
    textKo:
      '처음 만든 기억 유리에는 곡조 하나나 얼굴 하나 정도가 담겼습니다. 나중에는 지붕에 내리는 빗소리까지 방 하나를 통째로 보존했지요. 사람들은 그 소리를 듣겠다고 몇 시간씩 줄을 섰습니다.',
    voiceFile: 'N17.mp3',
  },
  'AGeri/Puzzles/Zone1/8-poly/0379.puz': {
    id: 'N18',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Every workshop had favourite shapes. Give me a shard with two particular bends and I could usually tell you who made it. The maker would then tell me I had the year wrong.',
    textKo:
      '작업실마다 즐겨 쓰는 모양이 있었습니다. 특정한 굴곡 두 개만 보여도 대개 누가 만든 조각인지 알 수 있었지요. 그러면 만든 사람은 제가 제작 연도를 틀렸다고 지적하곤 했습니다.',
    voiceFile: 'N18.mp3',
  },
  'AGeri/Puzzles/Zone1/8-poly/0380.puz': {
    id: 'N19',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I kept the original designs, the vidimus, for thousands of windows. Every alteration was supposed to come through my desk. You can imagine how popular that made me with the artists.',
    textKo:
      '저는 수천 개의 창에 대한 원본 도안, 비디무스를 보관했습니다. 무엇 하나 바꿀 때도 제 책상을 거쳐야 했지요. 장인들이 저를 얼마나 좋아했을지 짐작하시겠군요.',
    voiceFile: 'N19.mp3',
  },
  'AGeri/Puzzles/Zone1/10-same-shape-no-touch/0179B.puz': {
    id: 'N20',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'On one street, a cooper lived beside a music teacher and a woman who repaired clocks. Each complained about the other two. None wanted a different neighbour.',
    textKo:
      '어느 거리에는 나무통을 만드는 사람 옆에 음악 선생이, 그 옆에는 시계를 고치는 여인이 살았습니다. 셋은 서로가 시끄럽다고 불평했지요. 이웃을 바꾸고 싶다는 사람은 없었습니다.',
    voiceFile: 'N20.mp3',
  },
  'AGeri/Puzzles/Zone1/10-same-shape-no-touch/0183.puz': {
    id: 'N21',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We began linking windows so a memory could be shared between them. At first, you could hear a neighbour\'s wedding bells and still know perfectly well whose wedding it was.',
    textKo:
      '우리는 창들을 연결해 기억을 서로 나누기 시작했습니다. 처음에는 이웃의 결혼식 종소리를 들어도, 그것이 누구의 결혼식인지 분명히 알 수 있었지요.',
    voiceFile: 'N21.mp3',
  },
  'AGeri/Puzzles/Zone1/10-same-shape-no-touch/0159.puz': {
    id: 'N22',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Then a woman came home from the market and asked why her childhood house had been demolished. It had not. She was describing the house her neighbour had grown up in.',
    textKo:
      '그러다 한 여인이 장터에서 돌아와, 어릴 때 살던 집을 왜 허물었느냐고 물었습니다. 그 여인의 집은 그대로였습니다. 그녀가 설명하는 것은 이웃이 어린 시절 살았던 집이었지요.',
    voiceFile: 'N22.mp3',
  },
  'AGeri/Puzzles/Zone1/11-mixed-rules/0253.puz': {
    id: 'N23',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The windows out here were older, and their records were often incomplete. A date, a maker\'s name, sometimes just a price. I used to complain about the missing paperwork.',
    textKo:
      '이곳의 창들은 더 오래됐고, 기록도 불완전한 경우가 많았습니다. 날짜나 제작자 이름, 때로는 가격만 적혀 있었지요. 저는 서류가 빠졌다고 불평하곤 했습니다.',
    voiceFile: 'N23.mp3',
  },
  'AGeri/Puzzles/Zone1/11-mixed-rules/1171.puz': {
    id: 'N24',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'People began waking with songs they had never learned. I entered the first reports under a new heading: the Bleeding. At the time, I expected one folder to be enough.',
    textKo:
      '사람들이 배운 적 없는 노래를 기억하며 잠에서 깨기 시작했습니다. 저는 첫 보고서들을 새 항목 아래 넣었습니다. ‘스며듦’이라는 이름이었고, 당시에는 서류철 하나면 충분할 줄 알았지요.',
    voiceFile: 'N24.mp3',
  },
  'AGeri/Puzzles/Zone2/1-area-numbers/0552.puz': {
    id: 'N25',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We measured every pane we could reach and made excellent tables. I spent an entire evening correcting the totals. None of it explained why people were getting worse.',
    textKo:
      '손이 닿는 창은 모두 측정해서 잘 정리된 표로 만들었습니다. 저는 어느 날 저녁 내내 합계를 고쳤지요. 그래도 사람들이 왜 더 나빠지는지는 설명하지 못했습니다.',
    voiceFile: 'N25.mp3',
  },
  'AGeri/Puzzles/Zone2/1-area-numbers/0553.puz': {
    id: 'N26',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The memories were travelling through the links between windows. A perfectly sound pane could receive more than its maker had ever put into it. We had been inspecting each window on its own.',
    textKo:
      '기억은 창 사이의 연결을 타고 이동하고 있었습니다. 멀쩡한 창에도 제작자가 넣은 것보다 훨씬 많은 기억이 들어올 수 있었지요. 우리는 창을 하나씩 따로 살피고만 있었습니다.',
    voiceFile: 'N26.mp3',
  },
  'AGeri/Puzzles/Zone2/2-palisade/1116.puz': {
    id: 'N27',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We put lead and stone between the windows and moved some into empty buildings. We thought distance would weaken the links. There were masons working after midnight all over the city.',
    textKo:
      '우리는 창 사이를 납과 돌로 막고, 일부는 빈 건물로 옮겼습니다. 멀리 떨어뜨리면 연결이 약해질 거라고 생각했지요. 온 도시에서 석공들이 자정을 넘겨 일했습니다.',
    voiceFile: 'N27.mp3',
  },
  'AGeri/Puzzles/Zone2/2-palisade/1117.puz': {
    id: 'N28',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'For several weeks, there were fewer reports. I took two days away from the archive and slept through most of them. I remember being annoyed that I had wasted my holiday.',
    textKo:
      '몇 주 동안은 보고가 줄었습니다. 저는 이틀 휴가를 내고는 거의 내내 잠만 잤지요. 휴가를 낭비했다며 아쉬워했던 것이 기억납니다.',
    voiceFile: 'N28.mp3',
  },
  'AGeri/Puzzles/Zone2/2-palisade/1118.puz': {
    id: 'N29',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Then a child described a locked room across the city, including a crack beneath its carpet. We lifted the carpet to check. Moving the windows had not broken their links.',
    textKo:
      '그러다 한 아이가 도시 반대편의 잠긴 방을 설명했습니다. 카펫 밑에 난 금까지 말해서, 직접 카펫을 들어 확인했지요. 창을 옮겨 놓아도 연결은 끊어지지 않았던 겁니다.',
    voiceFile: 'N29.mp3',
  },
  'AGeri/Puzzles/Zone2/3-all-regions-same/0319.puz': {
    id: 'N30',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The more alike two window designs were, the more easily memories crossed between them. We had spent years encouraging workshops to use standard patterns. My signature was on the recommendation.',
    textKo:
      '두 창의 도안이 비슷할수록 기억도 쉽게 건너갔습니다. 우리는 여러 해 동안 작업실에 표준 무늬를 쓰라고 권했지요. 그 권고문에는 제 서명이 있었습니다.',
    voiceFile: 'N30.mp3',
  },
  'AGeri/Puzzles/Zone2/3-all-regions-same/0602.puz': {
    id: 'N31',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'A man began setting an extra place at supper for a woman he remembered as his mother. His wife had never heard of her. They argued about it for three nights.',
    textKo:
      '한 남자가 어머니 몫이라며 저녁 식탁에 자리를 하나 더 차리기 시작했습니다. 아내는 그가 말하는 여인을 전혀 몰랐지요. 두 사람은 그 일로 사흘 밤을 다퉜습니다.',
    voiceFile: 'N31.mp3',
  },
  'AGeri/Puzzles/Zone2/3-all-regions-same/1095.puz': {
    id: 'N32',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'When his own mother arrived, he asked her name. He was polite, apparently, and offered her the spare chair. She had come because she was worried about him.',
    textKo:
      '친어머니가 찾아왔을 때, 그 남자는 이름을 물었습니다. 예의 바르게 빈 의자까지 권했다고 하더군요. 어머니는 아들이 걱정돼서 온 것이었습니다.',
    voiceFile: 'N32.mp3',
  },
  'AGeri/Puzzles/Zone2/4-all-regions-different/0283.puz': {
    id: 'N33',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We began changing patterns so no two windows matched. It slowed the Bleeding, but it also damaged some of the memories inside. We were learning what a shape could bear by getting it wrong.',
    textKo:
      '우리는 서로 일치하는 창이 없도록 무늬를 바꾸기 시작했습니다. 스며듦은 느려졌지만, 안에 담긴 기억까지 상하는 경우가 있었지요. 모양을 얼마나 바꿔도 되는지, 망가뜨려 가며 배운 셈입니다.',
    voiceFile: 'N33.mp3',
  },
  'AGeri/Puzzles/Zone2/4-all-regions-different/0760.puz': {
    id: 'N34',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'People started carrying notebooks with their names and families written inside. Mine fitted in a coat pocket. I checked it before answering letters, especially letters from people I loved.',
    textKo:
      '사람들은 자기 이름과 가족을 적은 수첩을 가지고 다니기 시작했습니다. 제 것은 외투 주머니에 들어가는 크기였지요. 편지에 답하기 전에 확인했는데, 소중한 사람이 보낸 편지라면 더욱 그랬습니다.',
    voiceFile: 'N34.mp3',
  },
  'AGeri/Puzzles/Zone2/5-minmax/0556.puz': {
    id: 'N35',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We had tested how much memory one window could hold. We had never tested a whole city of connected windows. By then, some panes held traces of events from before their glass was made.',
    textKo:
      '창 하나가 얼마나 많은 기억을 담을 수 있는지는 시험했습니다. 하지만 도시 전체의 창을 연결한 상태로는 시험하지 않았지요. 그 무렵에는 유리가 만들어지기 전의 일까지 담긴 창이 있었습니다.',
    voiceFile: 'N35.mp3',
  },
  'AGeri/Puzzles/Zone2/5-minmax/0733.puz': {
    id: 'N36',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We preserved festivals, farewells, and afternoons when nobody did very much. When people asked whether one more memory would hurt, we usually said no. I had said it myself.',
    textKo:
      '우리는 축제도, 작별도, 아무 일 없이 보낸 오후도 보존했습니다. 기억 하나쯤 더 넣어도 괜찮겠느냐고 물으면 대개 괜찮다고 답했지요. 저도 그렇게 말했습니다.',
    voiceFile: 'N36.mp3',
  },
  'AGeri/Puzzles/Zone2/7-1SPR/0564.puz': {
    id: 'N37',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We moved the worst windows to small islands, each with a watcher. Distance bought us a little time, though it did not sever the links. Some watchers stayed clearheaded longer than people in the city.',
    textKo:
      '상태가 가장 나쁜 창은 작은 섬으로 옮기고 감시자를 붙였습니다. 거리가 연결을 끊지는 못했지만 시간은 조금 벌어 주었지요. 도시의 사람들보다 오래 맑은 정신을 유지한 감시자도 있었습니다.',
    voiceFile: 'N37.mp3',
  },
  'AGeri/Puzzles/Zone2/7-1SPR/0565.puz': {
    id: 'N38',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Their letters began with observations about the glass. After a while, they mostly asked for news from home. One man asked whether the bakery still opened on Sundays.',
    textKo:
      '감시자들의 편지는 처음에는 유리의 상태를 보고하는 내용이었습니다. 시간이 지나자 고향 소식을 묻는 말이 대부분이 됐지요. 한 사람은 빵집이 아직 일요일에도 문을 여느냐고 물었습니다.',
    voiceFile: 'N38.mp3',
  },
  'AGeri/Puzzles/Zone2/7-1SPR/0639.puz': {
    id: 'N39',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'That watcher wrote, “Elias, tell my wife I still remember her. And tell her I have learned to mend my own socks.” I sent the whole letter. I thought she should have both pieces of news.',
    textKo:
      '그 감시자는 이렇게 썼습니다. “엘리아스, 아내에게 아직 기억하고 있다고 전해 줘요. 양말도 이제 혼자 꿰맨다고요.” 저는 편지를 통째로 보냈습니다. 두 소식 모두 전해야 할 것 같았거든요.',
    voiceFile: 'N39.mp3',
  },
  'AGeri/Puzzles/Zone2/6-same-size-no-touch/0559.puz': {
    id: 'N40',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We sorted memories by size, then tried sorting them by importance. People kept asking us to move their ordinary afternoons into the important pile. In the end, I changed the labels.',
    textKo:
      '우리는 기억을 크기별로 나누다가 중요도에 따라서도 나눠 보았습니다. 사람들은 평범한 오후의 기억을 중요한 쪽으로 옮겨 달라고 거듭 부탁했지요. 결국 제가 분류표를 바꿨습니다.',
    voiceFile: 'N40.mp3',
  },
  'AGeri/Puzzles/Zone2/6-same-size-no-touch/0601.puz': {
    id: 'N41',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The king\'s daughter asked us to save a morning when her father taught her to whistle. The coronation already had six windows. She said one of those could wait.',
    textKo:
      '왕의 딸은 아버지가 휘파람 부는 법을 가르쳐 준 아침을 남겨 달라고 했습니다. 대관식을 담은 창은 이미 여섯 개였지요. 그중 하나쯤은 나중에 해도 된다고 하더군요.',
    voiceFile: 'N41.mp3',
  },
  'AGeri/Puzzles/Zone2/8-all-rectangles/0569.puz': {
    id: 'N42',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The architects proposed rectangular panes throughout the archive. They had proposed rectangles for several unrelated problems that year. Still, they brought drawings, and we needed something to try.',
    textKo:
      '건축가들은 기록 보관소의 유리를 전부 사각형으로 만들자고 했습니다. 그해 서로 상관없는 다른 문제에도 여러 번 사각형을 제안한 사람들이었지요. 그래도 도면을 가져왔고, 우리에게는 시도할 것이 필요했습니다.',
    voiceFile: 'N42.mp3',
  },
  'AGeri/Puzzles/Zone2/8-all-rectangles/0570.puz': {
    id: 'N43',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We rebuilt one room in three days. It looked like a cupboard designed by someone who disliked cupboards. I approved it anyway.',
    textKo:
      '우리는 사흘 만에 방 하나를 다시 만들었습니다. 찬장을 싫어하는 사람이 설계한 찬장처럼 생겼더군요. 저는 그래도 승인했습니다.',
    voiceFile: 'N43.mp3',
  },
  'AGeri/Puzzles/Zone2/8-all-rectangles/0571.puz': {
    id: 'N44',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The rectangular panes failed by Thursday. Wednesday evening, actually. I filed the report the next morning. There was some disagreement about whether that counted as four days of success.',
    textKo:
      '사각형 유리는 목요일에 실패했습니다. 정확히는 수요일 저녁이었고, 제가 보고서를 낸 것이 다음 날 아침이었지요. 성공한 기간을 나흘로 쳐도 되느냐를 두고 의견이 갈렸습니다.',
    voiceFile: 'N44.mp3',
  },
  'AGeri/Puzzles/Zone2/9-no-rectangles/0478.puz': {
    id: 'N45',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The next committee banned rectangles. The new room was harder to build, harder to clean, and no better at containing memories. I missed the cupboard.',
    textKo:
      '다음 위원회는 사각형을 금지했습니다. 새 방은 만들기도, 청소하기도 더 어려웠고, 기억을 가둬 두는 능력도 나아지지 않았지요. 저는 찬장이 그리웠습니다.',
    voiceFile: 'N45.mp3',
  },
  'AGeri/Puzzles/Zone2/9-no-rectangles/0574.puz': {
    id: 'N46',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Both proposals carry my approval stamp. I left them in the archive with the successful work. Anyone reading our records ought to know what we tried, including the embarrassing parts.',
    textKo:
      '두 제안서에는 모두 제 승인 도장이 찍혀 있습니다. 저는 성공한 작업들과 함께 그것들을 보관소에 남겼지요. 우리 기록을 읽는 사람은 부끄러운 시도까지도 알아야 하니까요.',
    voiceFile: 'N46.mp3',
  },
  'AGeri/Puzzles/Zone2/10-zone2-mixed/1203.puz': {
    id: 'N47',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The final meetings took place in the castle. We began each one by reminding everyone why they were there. Sometimes we had to do it again before the meeting ended.',
    textKo:
      '마지막 회의들은 성에서 열렸습니다. 매번 참석자들에게 왜 모였는지 알려 주는 것으로 시작했지요. 회의가 끝나기 전에 다시 알려 줘야 할 때도 있었습니다.',
    voiceFile: 'N47.mp3',
  },
  'AGeri/Puzzles/Zone2/10-zone2-mixed/0328.puz': {
    id: 'N48',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Before I go further: the designs you are following leave the old links broken. I tested them before leaving them here. Your repairs will not start the Bleeding again.',
    textKo:
      '이야기를 더 하기 전에 말씀드려야겠군요. 그대가 따르는 도안은 옛 연결이 끊어진 상태를 유지하도록 제가 시험해 둔 것입니다. 그대의 복원이 스며듦을 다시 일으키지는 않습니다.',
    voiceFile: 'N48.mp3',
  },
  'AGeri/Puzzles/Zone2/10-zone2-mixed/0300.puz': {
    id: 'N49',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The Shattering happened across the city in a single night. That much survived in the records. It was not an accident.',
    textKo:
      '대파손은 하룻밤 사이에 도시 전체에서 일어났습니다. 기록에도 그 사실은 남아 있지요. 사고는 아니었습니다.',
    voiceFile: 'N49.mp3',
  },
  'AGeri/Puzzles/Zone3/1-tatami/0612.puz': {
    id: 'N50',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'We chose the oldest linked window for one final test. Moving it had done nothing, and altering it had made things worse. We cleared the room around it.',
    textKo:
      '마지막 시험에는 가장 오래된 연결 창을 골랐습니다. 옮겨도 소용이 없었고, 고치려다가는 상태가 더 나빠졌지요. 우리는 그 창 주변을 비웠습니다.',
    voiceFile: 'N50.mp3',
  },
  'AGeri/Puzzles/Zone3/1-tatami/0037.puz': {
    id: 'N51',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I had looked after that window for most of my working life. I knew every old repair and which tools should never come near it. Someone handed me one of those tools.',
    textKo:
      '저는 그 창을 거의 평생 관리했습니다. 예전에 수리한 자리도 모두 알았고, 가까이 가져가서는 안 되는 도구도 알았지요. 누군가 제게 그 도구 하나를 건넸습니다.',
    voiceFile: 'N51.mp3',
  },
  'AGeri/Puzzles/Zone3/1-tatami/0656.puz': {
    id: 'N52',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I broke it with a hammer. The first blow only cracked a corner, so I had to strike it again. I remember that more clearly than I would like.',
    textKo:
      '저는 망치로 창을 깼습니다. 처음에는 모서리에 금만 가서 한 번 더 내리쳐야 했지요. 그 순간은 원치 않을 만큼 선명하게 기억납니다.',
    voiceFile: 'N52.mp3',
  },
  'AGeri/Puzzles/Zone3/2-loopy/0665.puz': {
    id: 'N53',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'A woman in the next room stopped speaking halfway through a sentence. Then she asked for her own daughter, using the right name. It was the first time in months.',
    textKo:
      '옆방의 여인이 말을 하다 멈췄습니다. 그러고는 자기 딸을, 정확한 이름으로 불렀지요. 몇 달 만에 처음 있는 일이었습니다.',
    voiceFile: 'N53.mp3',
  },
  'AGeri/Puzzles/Zone3/2-loopy/0666.puz': {
    id: 'N54',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The broken pieces still held memories, but they no longer passed them on. We checked the linked windows through the night. For once, the next report brought no new case.',
    textKo:
      '깨진 조각에는 기억이 남아 있었지만, 더는 다른 창으로 건너가지 않았습니다. 우리는 밤새 연결된 창들을 확인했지요. 모처럼 다음 보고에 새 환자가 없었습니다.',
    voiceFile: 'N54.mp3',
  },
  'AGeri/Puzzles/Zone3/2-loopy/0657.puz': {
    id: 'N55',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I sent the order to every workshop in Glimmith. We were to break all the memory-glass before morning. The order was mine, Artisan.',
    textKo:
      '저는 글리미스의 모든 작업실에 명령을 보냈습니다. 아침이 오기 전에 기억 유리를 전부 깨뜨리라는 것이었지요. 제가 내린 명령입니다, 장인.',
    voiceFile: 'N55.mp3',
  },
  'AGeri/Puzzles/Zone3/5-inequality/0578.puz': {
    id: 'N56',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'People called me a coward, a destroyer, and several things I had to look up. I kept their letters. They belonged in the record as much as my orders did.',
    textKo:
      '사람들은 저를 겁쟁이, 파괴자, 그리고 뜻을 찾아봐야 하는 몇 가지 이름으로 불렀습니다. 저는 그 편지들을 보관했습니다. 제 명령서만큼이나 기록에 남아야 할 것들이었지요.',
    voiceFile: 'N56.mp3',
  },
  'AGeri/Puzzles/Zone3/5-inequality/0728.puz': {
    id: 'N57',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'One man struck me outside the archive after we broke his wedding window. Later, he asked me to write down his wife\'s name before he lost it again. I found him a pencil.',
    textKo:
      '결혼식 창을 깨뜨렸다는 이유로 보관소 앞에서 저를 때린 남자가 있었습니다. 나중에는 아내의 이름을 또 잊기 전에 적어 달라고 부탁하더군요. 저는 연필을 찾아왔습니다.',
    voiceFile: 'N57.mp3',
  },
  'AGeri/Puzzles/Zone3/4-difference/0609.puz': {
    id: 'N58',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'By morning, the reports of borrowed memories had almost stopped. We waited for another wave, but none came. People began sleeping again.',
    textKo:
      '아침이 되자 남의 기억이 들어온다는 보고는 거의 멈췄습니다. 우리는 다시 시작될까 봐 기다렸지만, 그런 일은 없었지요. 사람들은 다시 잠을 자기 시작했습니다.',
    voiceFile: 'N58.mp3',
  },
  'AGeri/Puzzles/Zone3/4-difference/0587.puz': {
    id: 'N59',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Some memories returned, but not all of them. Mara remembered her favourite bench and asked who had taken it away. She did not recognise me when I answered.',
    textKo:
      '돌아온 기억도 있었지만, 모두 돌아오지는 않았습니다. 마라는 좋아하던 벤치를 기억하고는 누가 가져갔느냐고 물었지요. 제가 답했을 때, 저를 알아보지는 못했습니다.',
    voiceFile: 'N59.mp3',
  },
  'AGeri/Puzzles/Zone3/3-vertex-radar/0540.puz': {
    id: 'N60',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Airships carried people away for weeks. They took clothes, tools, recipes, and all the children who needed reminding not to lean over the rails. There was a great deal to organise.',
    textKo:
      '몇 주 동안 비행선들이 사람들을 실어 날랐습니다. 사람들은 옷과 도구와 요리법을 챙겼고, 난간 밖으로 몸을 내밀지 말라는 말을 거듭 들어야 하는 아이들도 데려갔지요. 챙길 일이 아주 많았습니다.',
    voiceFile: 'N60.mp3',
  },
  'AGeri/Puzzles/Zone3/3-vertex-radar/0539.puz': {
    id: 'N61',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Some families took plain glass for their new homes. You could look through it without hearing a voice or remembering someone else\'s kitchen. After everything, that was a comfort.',
    textKo:
      '새집에 쓸 평범한 유리를 가져간 가족도 있었습니다. 목소리가 들리거나 남의 부엌이 떠오르는 일 없이, 그냥 밖을 내다볼 수 있는 유리였지요. 그 일을 겪고 나니 그것만으로도 마음이 놓였습니다.',
    voiceFile: 'N61.mp3',
  },
  'AGeri/Puzzles/Zone3/3-vertex-radar/0542.puz': {
    id: 'N62',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'There was a seat for me on the last ship. I said I needed another week to finish sorting the fragments. The captain said there would not be another ship, and I stayed anyway.',
    textKo:
      '마지막 비행선에도 제 자리가 있었습니다. 저는 파편 분류를 끝내려면 일주일만 더 필요하다고 했지요. 선장은 다음 배가 없다고 했지만, 저는 남았습니다.',
    voiceFile: 'N62.mp3',
  },
  'AGeri/Puzzles/Zone3/6-compass/0885.puz': {
    id: 'N63',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The sorting took longer than a week. I had boxes for voices, rooms, and things I could not identify. The last category eventually needed its own room.',
    textKo:
      '분류에는 일주일보다 더 오래 걸렸습니다. 목소리, 방, 그리고 정체를 알 수 없는 것들을 나눠 상자에 담았지요. 마지막 항목은 결국 방 하나를 따로 써야 했습니다.',
    voiceFile: 'N63.mp3',
  },
  'AGeri/Puzzles/Zone3/6-compass/0887.puz': {
    id: 'N64',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'One fragment held the taste of a pear. I spent several evenings trying to remember whose orchard it came from. Eventually, I labelled it “pear” and let myself enjoy it.',
    textKo:
      '어느 조각에는 배 맛이 담겨 있었습니다. 누구의 과수원에서 난 배인지 떠올리려고 며칠 저녁을 보냈지요. 결국 ‘배’라고만 적어 놓고, 그냥 그 맛을 즐기기로 했습니다.',
    voiceFile: 'N64.mp3',
  },
  'AGeri/Puzzles/Zone3/6-compass/0888.puz': {
    id: 'N65',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I began testing ways to restore a window without reconnecting it to the others. A small one kept a kettle\'s whistle for a month without passing it on. I must have checked it a hundred times.',
    textKo:
      '다른 창과 다시 연결하지 않고도 창을 복원하는 방법을 시험하기 시작했습니다. 작은 창 하나가 주전자 소리를 한 달 동안 혼자 간직했지요. 백 번은 확인했을 겁니다.',
    voiceFile: 'N65.mp3',
  },
  'AGeri/Puzzles/Zone3/6-compass-main/1016.puz': {
    id: 'N66',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I kept the shapes that held each memory and removed the links that let it escape. Those are the revised designs you have been using. The kettle was my first success.',
    textKo:
      '기억을 담는 형태는 유지하고, 기억이 빠져나가는 연결은 없앴습니다. 그대가 사용해 온 것이 그렇게 수정한 도안이지요. 주전자 소리가 첫 성공이었습니다.',
    voiceFile: 'N66.mp3',
  },
  'AGeri/Puzzles/Zone3/6-compass-main/1017.puz': {
    id: 'N67',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'With more fragments in place, I found I could see the bridge again. I could even walk along it, counting the worn stones. I had crossed it for years without noticing them.',
    textKo:
      '더 많은 파편을 맞추자 다리가 다시 보였습니다. 닳은 돌의 수를 세며 그 위를 걸을 수도 있었지요. 여러 해 동안 건넜으면서도 눈여겨본 적 없던 돌들이었습니다.',
    voiceFile: 'N67.mp3',
  },
  'AGeri/Puzzles/Zone3/6-compass-main/0500.puz': {
    id: 'N68',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'At the far end, I heard a cart coming and stepped aside. Nothing passed me. The sound continued a little longer, then began again.',
    textKo:
      '다리 끝에서 수레가 오는 소리가 들려 비켜섰습니다. 아무것도 지나가지 않았지요. 소리는 조금 더 이어지더니 처음부터 다시 들렸습니다.',
    voiceFile: 'N68.mp3',
  },
  'AGeri/Puzzles/Zone3/7-finalboss/1152.puz': {
    id: 'N69',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The glass had kept more than voices and faces. It had kept the places around them: a street, a doorway, the view from somebody\'s kitchen. Enough pieces could make those places visible again.',
    textKo:
      '유리에는 목소리와 얼굴만 남은 것이 아니었습니다. 거리, 문간, 누군가의 부엌에서 보던 풍경도 함께 남아 있었지요. 조각이 충분히 모이면 그 장소를 다시 볼 수 있었습니다.',
    voiceFile: 'N69.mp3',
  },
  'AGeri/Puzzles/Data/FinalNote': {
    id: 'N70',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'At first, I thought the market had somehow survived. Then I heard the same dropped spoon three times, with the same laugh after it. I stayed to listen a fourth time.',
    textKo:
      '처음에는 장터가 어떻게든 남아 있는 줄 알았습니다. 그런데 숟가락을 떨어뜨리는 소리가 세 번 똑같이 들렸고, 뒤따르는 웃음소리도 같았지요. 저는 네 번째 소리까지 듣고 왔습니다.',
    voiceFile: 'N70.mp3',
  },
  'AGeri/Puzzles/Data/FinalNote2': {
    id: 'N71',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The Glimmith you are exploring is made from those surviving memories. This is where my repaired windows led me, too. I spent a long time walking these streets.',
    textKo:
      '그대가 둘러보는 글리미스는 그렇게 남은 기억으로 이루어져 있습니다. 저 역시 복원한 창을 통해 이곳에 왔지요. 이 거리들을 참 오래 걸었습니다.',
    voiceFile: 'N71.mp3',
  },
  'AGeri/Puzzles/Zone3/7-zone3-mixed/0616.puz': {
    id: 'N72',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The bridge, the market, the castle: each was preserved in pieces by people who lived here. They never meant to leave a whole kingdom behind. Most were saving something much smaller.',
    textKo:
      '다리도, 장터도, 성도 이곳에 살던 사람들이 조금씩 남긴 것입니다. 왕국 전체를 남기려던 것은 아니었지요. 대부분 훨씬 작은 무언가를 간직하려던 사람들이었습니다.',
    voiceFile: 'N72.mp3',
  },
  'AGeri/Puzzles/Zone3/7-zone3-mixed/0679.puz': {
    id: 'N73',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The people themselves left on the airships. The glass kept their rooms and sometimes their footsteps, but an open door does not mean someone is waiting inside. I checked a great many doors.',
    textKo:
      '사람들은 비행선을 타고 떠났습니다. 유리는 그들의 방과 때로는 발소리도 간직했지만, 문이 열려 있다고 안에 누군가 기다리는 것은 아니었지요. 저는 참 많은 문을 확인했습니다.',
    voiceFile: 'N73.mp3',
  },
  'AGeri/Puzzles/Zone3/7-zone3-mixed/0421.puz': {
    id: 'N74',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The records gave me dates and names. The smaller things—the baker counting colours, Mara laughing—have been coming back as you repair the windows. I did not know how much of them was missing.',
    textKo:
      '기록에는 날짜와 이름이 남아 있었습니다. 하지만 제빵사가 색을 세던 모습이나 마라의 웃음 같은 작은 일들은, 그대가 창을 고칠 때마다 돌아왔지요. 그렇게 많이 잊고 있었는지도 몰랐습니다.',
    voiceFile: 'N74.mp3',
  },
  'AGeri/Puzzles/Zone3/7-zone3-mixed/0493.puz': {
    id: 'N75',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'There is one last record in a garden beyond the mist. I made it after the rest of the archive was finished. I have been putting off taking you there.',
    textKo:
      '안개 너머 정원에 마지막 기록이 하나 있습니다. 나머지 기록을 모두 정리한 뒤에 만든 것이지요. 그대를 그곳으로 안내하는 일을 자꾸 미루고 있었습니다.',
    voiceFile: 'N75.mp3',
  },
  'AGeri/Puzzles/Zone3/7-zone3-mixed/1107.puz': {
    id: 'N76',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I used to eat my lunch in that garden when the work became too much. There was no important ceremony there, and no famous window. It was simply somewhere I liked.',
    textKo:
      '일이 버거울 때면 그 정원에서 점심을 먹곤 했습니다. 중요한 의식이 열린 곳도, 유명한 창이 있는 곳도 아니었지요. 그저 제가 좋아하는 장소였습니다.',
    voiceFile: 'N76.mp3',
  },
  'AGeri/Puzzles/Zone3/7-zone3-mixed/1102.puz': {
    id: 'N77',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'When you reach the garden, I would like you to hear that last record with me. I have spent a long time telling you about other people. This part is harder.',
    textKo:
      '정원에 도착하면 마지막 기록을 저와 함께 들어 주셨으면 합니다. 오랫동안 다른 사람들의 이야기를 들려드렸군요. 이번 이야기는 조금 어렵습니다.',
    voiceFile: 'N77.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/0154.puz': {
    id: 'N78',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'You have come a long way with me, Artisan. I had intended to keep to dates, designs, and useful instructions. Somehow, I have told you rather a lot about my neighbours.',
    textKo:
      '참 먼 길을 함께 왔군요, 장인. 원래는 날짜와 도안, 필요한 설명만 이야기하려고 했습니다. 어쩌다 보니 이웃들 이야기를 꽤 많이 했군요.',
    voiceFile: 'N78.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/1109.puz': {
    id: 'N79',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I carried a chair into this garden when I could no longer manage the stairs. The archive was finished by then. For the first time in years, I had nowhere I needed to be.',
    textKo:
      '계단을 오르내리기 어려워졌을 때, 이 정원에 의자를 가져다 놓았습니다. 기록 정리는 그 무렵 끝나 있었지요. 여러 해 만에 처음으로 꼭 가야 할 곳이 없었습니다.',
    voiceFile: 'N79.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/0680.puz': {
    id: 'N80',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I lived in Glimmith for nineteen years after the last ship left. Near the end, I began leaving notes beside unfinished tasks. Some mornings, I could not remember writing them.',
    textKo:
      '마지막 배가 떠난 뒤 저는 글리미스에서 십구 년을 더 살았습니다. 마지막 무렵에는 끝내지 못한 일 옆에 메모를 남겼지요. 아침이 되면 제가 썼다는 사실이 기억나지 않을 때도 있었습니다.',
    voiceFile: 'N80.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/1085a.puz': {
    id: 'N81',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'There was no one left to take over the archive. So I made one final piece of memory-glass and gave it my memories and my voice. I hoped it could help whoever came next.',
    textKo:
      '기록을 이어서 관리할 사람은 남아 있지 않았습니다. 그래서 마지막 기억 유리를 만들어 제 기억과 목소리를 남겼지요. 다음에 오는 누군가에게 도움이 되기를 바랐습니다.',
    voiceFile: 'N81.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/1322.puz': {
    id: 'N82',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I died here, Artisan. The voice you have followed is what the glass kept of Elias Vidimus. There is no one waiting for you further on.',
    textKo:
      '저는 이곳에서 죽었습니다, 장인. 그대가 따라온 목소리는 유리에 남은 엘리아스 비디무스입니다. 더 안쪽에서 그대를 기다리는 사람은 없습니다.',
    voiceFile: 'N82.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/0897fix.puz': {
    id: 'N83',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'I left instructions and a record of what happened. I did not leave myself Mara\'s laugh. That came back while you were here. You gave me something I had not expected to hear again.',
    textKo:
      '저는 설명과 사건의 기록을 남겼지만, 마라의 웃음소리는 남기지 못했습니다. 그것은 그대와 함께 있는 동안 돌아왔지요. 다시는 듣지 못할 줄 알았던 소리를 그대가 돌려주었습니다.',
    voiceFile: 'N83.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/0932.puz': {
    id: 'N84',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The shapes kept those memories intact. Your careful work brought them back. I know I have been particular about the rules. There were people in those details, and I did not want to lose any more of them.',
    textKo:
      '형태가 그 기억들을 지켜 주었고, 그대가 정성껏 맞춘 덕분에 다시 돌아왔습니다. 제가 규칙을 꽤 까다롭게 따졌지요. 그 작은 부분들에 사람들이 남아 있었고, 저는 더 잃고 싶지 않았습니다.',
    voiceFile: 'N84.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/0941.puz': {
    id: 'N85',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The baker wanted twelve shades of amber, but five still kept her story. Your colours can be different again. I expect she would have counted them, then asked you to make one more.',
    textKo:
      '그 제빵사는 열두 가지 호박색을 원했지만, 다섯 가지 색으로도 이야기는 남았습니다. 그대는 또 다른 색을 써도 됩니다. 아마 그 여인은 색을 다 세어 본 뒤 하나만 더 넣어 달라고 했을 겁니다.',
    voiceFile: 'N85.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/0988.puz': {
    id: 'N86',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'Thank you for staying to listen, Artisan. It has been a long time since I had anyone to tell these stories to. I am glad I remembered the baker before you left.',
    textKo:
      '이야기를 끝까지 들어 주어 고맙습니다, 장인. 이런 이야기를 들려줄 사람이 참 오랜만이었군요. 그대가 떠나기 전에 그 제빵사가 생각나서 다행입니다.',
    voiceFile: 'N86.mp3',
  },
  'AGeri/Puzzles/Zone3/8-endgame/0268.puz': {
    id: 'N87',
    trigger: 'HasBeenSolved',
    verified: true,
    textEn:
      'The shapes are ours, Artisan. The colours are yours.',
    textKo:
      '형태는 우리의 것입니다, 장인. 색은 그대의 것입니다.',
    voiceFile: 'N87.mp3',
  },
};
