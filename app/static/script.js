var planetarium1;
S(document).ready(function() {
	var planetarium1 = S.virtualsky({
			id: 'skymap',
      'projection': 'gnomic',
      //'ra': 83.8220833,
      //'dec': -5.3911111,
      showplanets: true,
      width: 800,
      height: 800,
      'constellations': true,
      constellationlabels: true,
      lang: 'es',
      fontsize: '18px',
      clock: new Date("December 12, 2020 01:21:00"),
	});

  planetarium1.addPointer({
		'ra':83.8220792,
		'dec':-5.3911111,
		'label':'Orion Nebula',
		'img':'http://server7.sky-map.org/imgcut?survey=DSS2&w=128&h=128&ra=5.58813861333333&de=-5.3911111&angle=1.25&output=PNG',
		'url':'http://simbad.u-strasbg.fr/simbad/sim-id?Ident=M42',
		'credit':'Wikisky',
		'colour':'rgb(255,220,220)'
	})
});