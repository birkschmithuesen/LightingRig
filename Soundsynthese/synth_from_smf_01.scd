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



SynthDef(\trigger, {
	arg amp = 0.2, gate = 0, freq = 400, xpos = 0, ypos = 0;
    var sig, env;
	env = EnvGen.kr(Env.perc(attackTime:0.01, releaseTime:0.1), gate);
    sig = SinOsc.ar(freq, 0, 0.1);
	sig = sig * env * amp;
	sig = Pan4.ar(sig, xpos, ypos);
    Out.ar(0, sig)
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
~numLights.do{arg i; ~synths[i].set(\freq, 60 + i.linexp(0, 16, 1.0, 500.0).postln);};
~numLights.do{arg i; ~trigger[i].set(\freq, 60 + i.linexp(0, 16, 400.0, 600.0));};


s.meter;
s.plotTree;
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
		~synths[i].set(\tremolo, msg[i+1].linlin(-1.0, 1.0, 1.0, 50.0));
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


~numLights.do{arg i; ~synths[i].set(\amp, 0.02;)};

~numLights.do{arg i; ~trigger[i].set(\amp, 0.5;)};