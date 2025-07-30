```supercollider

(
// SynthDef for the test tone generator
SynthDef(\testTone, {
    arg freq=440, amp=0.5, waveform=0, gate=1, ch=0, posX=0, posY;
    var sig, env, quad, rotated;

    // Select the waveform type
    sig = Select.ar(waveform, [
        SinOsc.ar(freq),  // Sine wave
        Saw.ar(freq),    // Sawtooth wave
        Pulse.ar(freq),  // Pulse wave
        LFTri.ar(freq)   // Triangular wave
    ]);

    // Envelope generator
    env = EnvGen.kr(Env.adsr(0.01, 0.1, 0.8, 0.1), gate, doneAction: 2);

	rotated = ~rotateXY.(posX, posY); //rotate if speakers are heanging in different position

    // Quadrophonic panning
    quad = Pan4.ar(sig * env * amp, rotated[0], rotated[1]);

    // Output the sound
	Out.ar(ch, [quad[3], quad[0], quad[2], quad[1]]);//[quad[1], quad[3], quad[2], quad[0]]);
}).add;


~rotateXY = { |x, y|
    var angle = -pi/4;
    [
        x * cos(angle) - y * sin(angle),
        x * sin(angle) + y * cos(angle)
    ]
};


// GUI for the sound tester
Window("Sound Tester", Rect(100, 100, 300, 260)).front.layout_(
    VLayout(
        HLayout(
            StaticText().string_("Freq:"),
            Slider().action_({|sl| ~testSynth.set(\freq, sl.value.linexp(0,1,100,2000)); })
        ),
        HLayout(
            StaticText().string_("Amp:"),
            Slider().action_({|sl| ~testSynth.set(\amp, sl.value); })
        ),
        HLayout(
            StaticText().string_("Wave:"),
            PopUpMenu().items_(["Sine","Saw","Pulse","Tri"]).action_({|pm| ~testSynth.set(\waveform, pm.value); })
        ),
        HLayout(
            StaticText().string_("Channel:"),
            PopUpMenu().items_(["0","1","2","3"]).action_({|pm| ~testSynth.set(\ch, pm.value); })
        ),
        HLayout(
            StaticText().string_("posX:"),
            Slider().action_({|sl| ~testSynth.set(\posX, sl.value.linlin(0,1,-1,1)); })
        ),
        HLayout(
            StaticText().string_("posY:"),
            Slider().action_({|sl| ~testSynth.set(\posY, sl.value.linlin(0,1,-1,1)); })
        ),
        Button().states_([["Play"],["Stop"]]).action_({|btn|
            if(btn.value==1) { ~testSynth = Synth(\testTone); } { ~testSynth.set(\gate,0); }
        })
    )
);
)


```