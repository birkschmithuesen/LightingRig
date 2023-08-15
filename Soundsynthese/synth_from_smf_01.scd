s.meter;


s.options.numOutputBusChannels = 4;
s.boot;

(
///////////////////////////////////
// setup
///////////////////////////////////
~numLights = 16;



///////////////////////////////////
// Synth Def
///////////////////////////////////

SynthDef(\base, {
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
	sig = Pan4.ar(sig, xpos, ypos);
	Out.ar(0, sig);
}).add;



///////////////////////////////////
// Synth section
///////////////////////////////////

// free all synths
//~numLights.do{arg i; ~synths[i].free;}

// create synths
~synths = {arg i; Synth.new(\base)}!~numLights;

//change pitches
~numLights.do{arg i; ~synths[i].set(\freq, 60 + (i * 100));};






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
		~synths[i].set(\tremolo, msg[i+1].linlin(-1.0, 1.0, 1.0, 20.0));
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
		~synths[i].set(\detune, msg[i+1].linlin(-1.0, 1.0, 0.9, 1.1));
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
	}
},
('/ty')
);

)

s.meter;
s.plotTree;

// (-1/-1) => (10 / 0)
//

~numLights.do{arg i; ~synths[i].set(\xpos, -1);}




)


/////////////////////////////////////////


(
a = {
	arg freq = 1, amp = 0.1;
	var sig;
	freq = 100 + (freq * 1000);
	sig = Saw.ar(freq, amp);
	Out.ar(0,[sig, sig]);
}.play;
)


a.set(\freq, 0.1);


a.map(1, ~tilt_degree);


/////////////////////////////////////////

(
// something to play with
SynthDef(\help_Bus, { arg out=0,ffreq=100;
    var x;
    x = RLPF.ar(LFPulse.ar(SinOsc.kr(0.2, 0, 10, 21), [0,0.1], 0.1),
            ffreq, 0.1)
            .clip2(0.4);
    Out.ar(out, x);
}).add;

)

x = Synth(\help_Bus);


