(() => {
  const adultAmmaMarkup = () => `<svg viewBox="0 0 180 300" aria-label="കേരളത്തിലെ അമ്മ" role="img">
    <g class="leg leg-a"><path d="M72 232l-8 52" stroke="#70433f" stroke-width="18" stroke-linecap="round"/><path d="M49 288h31" stroke="#283337" stroke-width="9" stroke-linecap="round"/></g>
    <g class="leg leg-b"><path d="M108 232l13 52" stroke="#70433f" stroke-width="18" stroke-linecap="round"/><path d="M108 288h33" stroke="#283337" stroke-width="9" stroke-linecap="round"/></g>
    <path class="body" d="M45 112Q90 96 135 112L151 232Q91 258 29 232Z" fill="#d88358"/>
    <path d="M43 137Q90 154 141 137L146 228Q91 248 35 228Z" fill="#db9a55"/>
    <path d="M48 157Q91 177 142 156M43 185Q91 204 146 183M39 212Q90 230 148 209" fill="none" stroke="#b95d4d" stroke-width="5"/>
    <path d="M120 111Q142 143 133 204L104 188Q113 147 96 116Z" fill="#edbb78" opacity=".95"/>
    <g class="arm arm-back"><path d="M47 122Q20 154 29 194" stroke="#9a594b" stroke-width="16" stroke-linecap="round" fill="none"/><circle cx="29" cy="198" r="10" fill="#9a594b"/></g>
    <g class="arm arm-front"><path d="M133 122Q160 153 148 194" stroke="#9a594b" stroke-width="16" stroke-linecap="round" fill="none"/><circle cx="148" cy="198" r="10" fill="#9a594b"/></g>
    <g class="head"><circle cx="90" cy="70" r="31" fill="#9a5a4d"/>
      <path d="M59 71Q58 25 91 23Q123 25 122 72Q106 51 61 72Z" fill="#252d31"/>
      <circle cx="121" cy="34" r="16" fill="#252d31"/><path d="M67 70Q76 75 84 70M97 70Q106 75 114 70" fill="none" stroke="#252d31" stroke-width="5" class="brow"/>
      <circle cx="77" cy="82" r="4" fill="#252d31" class="eye"/><circle cx="104" cy="82" r="4" fill="#252d31" class="eye"/>
      <path d="M82 98Q90 104 100 97" fill="none" stroke="#713e43" stroke-width="5" class="mouth"/>
      <path d="M61 55Q48 69 59 90M119 55Q132 69 121 90" fill="none" stroke="#e0a76a" stroke-width="5"/>
    </g>
  </svg>`;
  document.querySelectorAll('.amma').forEach((element) => { element.innerHTML = adultAmmaMarkup(); });
})();
