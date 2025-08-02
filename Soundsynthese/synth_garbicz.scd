s.meter;
ServerOptions.devices;
s.options.outDevice("3- ZOOM AMS-24 Driver");
s.options.outDevice("External Headphones");

s.options.numOutputBusChannels = 4;
s.options.numInputBusChannels = 0;

s.boot;

s.meter;
s.plotTree;


// Create 4 recorders (needs to be done just once in a session):
(
~recs = Recorder.new(s).dup(4)
~counter = 0;
)

// START ALL MONO RECORDERS (chans 0, 1, 2, 3)
(
var basicPath = "~/recordings/"+~counter; // customize this
~counter = ~counter + 1;
~recs.do({ arg thisRecorder, index;
	var fileName = "test" ++ index ++ ".wav";

	thisRecorder.record(
		path: basicPath ++ fileName,
		bus: index,
		numChannels: 1 // mono
	);
})
)

// Stop all recorders
~recs.do({ arg thisRecorder; thisRecorder.stopRecording })


(
///////////////////////////////////
// setup
///////////////////////////////////
~numLights = 16;



///////////////////////////////////
// Synth Def
///////////////////////////////////




SynthDef(\base, {
    arg freq=440, amp=5, exc = 0.1, xpos = 0, ypos = 0, filter_width = 0.03;
    var noise, sig;
    noise = WhiteNoise.ar(1) * 0.5 + PinkNoise.ar(1) * 0.5;
    sig = BPF.ar(noise, freq, filter_width * exc); // wider bandwidth = heavier
    //sig = sig.tanh * (0.3 - (exc * 0.1)) + sig.distort * (0.7 + (exc * 2)); // more distortion with excitation
    sig = sig * exc * amp * 10; // exc controls overall volume - 0 = silence
    //CombN.ar(sig, 0.31, 0.31, 2, 1, sig);
    sig = Pan4.ar(sig, xpos, ypos);
    Out.ar(0, [sig[3], sig[0], sig[2], sig[1]]);
}).add;




SynthDef(\trigger, {
	arg exc = 1.2, freq = 320, xpos = 0, ypos = 0, dens = 40, dev = 1.1, lfodepth = 300, decay = 0.3, gate = 0, delay_vol = 0.5, maxdelaytime = 0.2, delaytime = 0.12, distortion = 0.4, drive = 6.0, atk=0.1, sus=0.1, rel=5, c1=1, c2=(-1), detune=0.2, pan=0, cfmin=800, cfmax=800, rqmin=0.005, rqmax=0.008, lsf=200, ldb=0, amp=3, out=0, cfhzmin=0.1, cfhzmax=0.3;
    var sig, env, rotated, randomFreq;
	cfmin = freq;
	cfmax = freq;
	env = EnvGen.kr(Env.perc(attackTime:0.01, releaseTime:0.4), gate);
	sig = Saw.ar(freq * {LFNoise1.kr(0.5,detune).midiratio}!2);
	sig = BPF.ar(
		sig,
		{LFNoise1.kr(
			LFNoise1.kr(4).exprange(cfhzmin, cfhzmax)
		).exprange(cfmin, cfmax)}!2,
		{LFNoise1.kr(0.1).exprange(rqmin, rqmax)}!2
	);
	sig =BLowShelf.ar(sig, lsf, 0.5, ldb);
	sig = Balance2.ar(sig[0], sig[1], pan);
	sig = Mix(sig * env * amp);
	sig = Pan4.ar(sig, xpos, ypos);
	Out.ar(0, [sig[3], sig[0], sig[2], sig[1]]);
}).add;





///////////////////////////////////
// Synth section
///////////////////////////////////

// free all synths
//~numLights.do{arg i; ~synths[i].free;}

// create synths
~synths = {arg i; Synth.new(\base)}!~numLights;
~trigger = {arg i; Synth.new(\trigger)}!~numLights;

//change pitches
~dorianScale = [0, 3, 2, 7, 5, 10, 9];
~pentatonicScale = [0, 5, 3, 10, 7];
~scale = ~pentatonicScale;

~numLights.do{arg i; ~synths[i].set(\freq, 200 + i.linexp(0, 16, 200.0, 2000.0).postln);};

~numLights.do{arg i;
    var degree = i % 5;
    var octave = (i / 5).floor;
    var midiNote = ~scale[degree] + 60 + (octave * 12);
    ~synths[i].set(\freq, midiNote.midicps);
};


~numLights.do{arg i;
    var degree = i % 5;
    var octave = (i / 5).floor;
    var midiNote = ~scale[degree] + 48 + (octave * 12);
    ~trigger[i].set(\freq, midiNote.midicps);
};



~trigger[1].set(\gate,1);



///////////////////////////////////
// receive the OSC information
///////////////////////////////////


OSCFunc({
	arg msg;
	var val;
	//msg[1].postln;
	~numLights.do{
		arg i;
		~synths[i].set(\exc, msg[i+1]);
		//~trigger[i].set(\exc, msg[i+1]);
	}
},
('/vel')
);


OSCFunc({
	arg msg;
	var val;
	//msg[1].postln;
	~numLights.do{
		arg i;
		//~synths[i].set(\tremolo, msg[i+1].linlin(-1.0, 1.0, 1.0, 50.0));
	}
},
('/vel_tx')
);


OSCFunc({
	arg msg;
	var val;
	//msg[1].postln;
	~numLights.do{
		arg i;
		//~synths[i].set(\detune, msg[i+1].linlin(-1.0, 1.0, 0.9, 1.1));
	}
},
('/vel_ty')
);


OSCFunc({
	arg msg;
	var val;
	//msg[1].postln;
	~numLights.do{
		arg i;
		~synths[i].set(\xpos, msg[i+1]);
		~trigger[i].set(\xpos, msg[i+1]);
	}
},
('/tx')
);


OSCFunc({
	arg msg;
	var val;
	//msg[1].postln;
	~numLights.do{
		arg i;
		~synths[i].set(\ypos, msg[i+1]);
		~trigger[i].set(\ypos, msg[i+1]);
	}
},
('/ty')
);

OSCFunc({
	arg msg;
	var val;
	//msg[1].postln;
	~numLights.do{
		arg i;
		~trigger[i].set(\gate, msg[i+1]);
	}
},
('/colliding')
);

)

(
var synth, window, ampSlider, filterSlider, triggerAmpSlider, triggerFreqSlider, triggerDecaySlider;


// Create window
window = Window("Synth Controls", Rect(100, 100, 350, 600));
window.view.decorator = FlowLayout(window.view.bounds);

// BASE SYNTH CONTROLS
StaticText(window, 330@25).string_("=== BASE SYNTH ===").align_(\center);

// Amp control
StaticText(window, 330@20).string_("Amplitude");
ampSlider = EZSlider(window, 330@30, "Amp", ControlSpec(0, 10, \lin, 0.1, 5),
    { |slider| ~numLights.do{arg i; ~synths[i].set(\amp, slider.value);}; });

// Filter width control
StaticText(window, 330@20).string_("Filter Width");
filterSlider = EZSlider(window, 330@30, "Filter", ControlSpec(0.01, 0.1, \lin, 0.001, 0.03),
    { |slider| ~numLights.do{arg i; ~synths[i].set(\filter_width, slider.value);}; });

// TRIGGER SYNTH CONTROLS
StaticText(window, 330@25).string_("=== TRIGGER SYNTH ===").align_(\center);

// Trigger Amp control
StaticText(window, 330@20).string_("Amplitude");
triggerAmpSlider = EZSlider(window, 330@30, "T-Amp", ControlSpec(0, 5, \lin, 0.1, 1),
    { |slider| ~numLights.do{arg i; ~trigger[i].set(\amp, slider.value;)}; });


// Trigger Decay control
StaticText(window, 330@20).string_("Decay");
triggerDecaySlider = EZSlider(window, 330@30, "T-Decay", ControlSpec(0.01, 1.0, \lin, 0.01, 0.3),
	{ |slider| ~numLights.do{arg i; ~trigger[i].set(\decay, slider.value;)}; });

// Delay max time
StaticText(window, 330@20).string_("Delay");

triggerDecaySlider = EZSlider(window, 330@30, "Vol", ControlSpec(0.01, 1.0, \lin, 0.01, 0.5),
	{ |slider| ~numLights.do{arg i; ~trigger[i].set(\delay_vol, slider.value;)}; });

triggerDecaySlider = EZSlider(window, 330@30, "MaxTime", ControlSpec(0.01, 10.0, \lin, 0.01, 0.2),
	{ |slider| ~numLights.do{arg i; ~trigger[i].set(\maxdelaytime, slider.value;)}; });

// Delay time
triggerDecaySlider = EZSlider(window, 330@30, "Time", ControlSpec(0.01, 1.0, \lin, 0.01, 0.2),
	{ |slider| ~numLights.do{arg i; ~trigger[i].set(\delaytime, slider.value;)}; });

// Close action
window.onClose_({ synth.free });

// Show window
window.front;
)

0.8.lincurve(0,1,0,1,2);

~numLights.do{arg i; ~synths[i].set(\speed, 10;)};
~numLights.do{arg i; ~synths[i].set(\amp, 100;)};

~numLights.do{arg i; ~trigger[i].set(\amp, 0;)};



/*SynthDef(\base, {
	arg freq = 200, detune = 1.01, amp = 0.01, tremolo = 10, exc = 0.1, xpos = 0, ypos = 0;
	var sig;
	//tremolo = In.kr(~tilt_degree).linlin(0,1,5,100);
	//detune = In.kr(~pan_degree).linlin(0,1,1.01,2.0);
	//amp = In.kr(~tilt_speed);
	//tremolo = MouseY.kr(5, 200, 1);
	amp = (0.5 + SinOsc.kr(tremolo * 0.5)) * amp;
	//detune = MouseY.kr(1.01, 2.0);
	//amp = Saw.kr({ExpRand(1,3)}!2).range(0.2, 1) * amp;
	sig = Mix.ar({LFPulse.ar(freq * Rand(-1.0, 1.0).range(detune.reciprocal, detune))}!4);
	sig = sig * amp * exc;
	sig = FreeVerb.ar(sig);
	sig = Pan4.ar(sig, xpos, ypos);
	Out.ar(0, [sig[3], sig[0], sig[2], sig[1]]);
}).add;*/



/* V2
SynthDef(\trigger, {
	arg exc = 1, amp = 0.8, freq = 320, xpos = 0, ypos = 0, dens = 40, dev = 1.1, lfodepth = 300, decay = 0.3, gate = 0, delay_vol = 0.5, maxdelaytime = 0.2, delaytime = 0.12, distortion = 0.4, drive = 6.0;
    var sig, env, rotated, randomFreq;
	//gate = Impulse.ar(50);
	env = EnvGen.kr(Env.perc(attackTime:0.01, releaseTime:decay), gate);
	// Generate new random number each time gate triggers
    randomFreq = TRand.kr(lo: -4.0, hi: 4.0, trig: gate);
	sig = (0.8 * SinOsc.ar(freq)) + (0.2 * LFSaw.ar((freq/2)+randomFreq));
	sig = sig * env;
	// Add distortion before mixing
    sig = sig * drive; // boost signal before distortion
    sig = Select.ar(distortion > 0.5, [
        sig.tanh,              // soft distortion (distortion < 0.5)
        sig.distort           // hard distortion (distortion >= 0.5)
    ]);
    sig = sig * distortion.linlin(0, 1, 1, 0.3); // compensate volume

    sig = Mix.ar(sig) * exc * amp;

	sig = Mix.ar(sig) * exc * amp;
	sig = FreeVerb.ar(sig);
	//sig = CombN.ar(sig, maxdelaytime, delaytime, 2, 1, sig);
	sig = sig + (delay_vol * DelayC.ar(sig,maxdelaytime: maxdelaytime, delaytime: delaytime));
	sig = Pan4.ar(sig, xpos, ypos);
	Out.ar(0, [sig[3], sig[0], sig[2], sig[1]]);
}).add;*/

/* V1
SynthDef(\trigger, {
	arg amp = 0.2, gate = 0, freq = 400, xpos = 0, ypos = 0;
    var sig, env;
	env = EnvGen.kr(Env.perc(attackTime:0.01, releaseTime:0.1), gate);:
    sig = SinOsc.ar(freq, 0, 0.1);
	sig = sig * env * amp;
	sig = Pan4.ar(sig, xpos, ypos);
    Out.ar(0, sig)
}).add;
*/


