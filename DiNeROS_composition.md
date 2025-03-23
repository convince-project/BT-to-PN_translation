## Output example

How to send signal from a normal petri net to a signal place
```xml
<place id="ObjectPoolGreen">
	<toolspecific tool="de.tudresden.inf.st.pnml.distributedPN" version="0.1">
		<node>
			selector
		</node>
		<subnet>
			selectorGreen
		</subnet>
		<balloonMarking>
			<tokens>
				<token>
					{"color" : "red", "name" : "red1", "pickSuccess" : "false", "placeSuccess" : "false",
					"humanDetected" : "false", "sensorData" : "", "trace" : "", "locked" : "false" }
				</token>
			</tokens>
		</balloonMarking>
	</toolspecific>
	<initialMarking>
		<text>
			1
		</text>
	</initialMarking>
	<name>
		<text>
			ObjectPoolGreen
		</text>
	</name>
</place>

<arc id="a6" source="ObjectPoolGreen" target="SortGreen">
</arc>

<transition id="SortGreen">
	<toolspecific tool="de.tudresden.inf.st.pnml.distributedPN" version="0.1">
		<node>
			selector
		</node>
		<subnet>
			selectorGreen
		</subnet>
		<type>
			discreteTransitionType
		</type>
		<inputsignalclause>
			(Green)
		</inputsignalclause>
	</toolspecific>
	<name>
		<text>
			SortGreen
		</text>
	</name>
</transition>
```
## Input example

How to receive signal from a normal petri net to a signal place
```xml
<place id="SensorResponse">
    <toolspecific tool="de.tudresden.inf.st.pnml.distributedPN" version="0.1">
        <node>Executor</node>
        <subnet>SafetyModel</subnet>
    </toolspecific>
    <name>
        <text>SensorResponse</text>
    </name>
</place>

<transition id="TransitionUnsafe">
    <toolspecific tool="de.tudresden.inf.st.pnml.distributedPN" version="0.1">
        <node>Executor</node>
        <subnet>SafetyModel</subnet>
        <type>discreteTransitionType</type>
        <inputsignalclause></inputsignalclause>
    </toolspecific>
    <name>
        <text>TransitionUnsafe</text>
    </name>
</transition>

<arc id="a54" source="TransitionUnsafe" target="Unsafe">
</arc>
<arc id="a53" source="SensorResponse" target="TransitionUnsafe">
</arc>

<place id="Unsafe">
    <toolspecific tool="de.tudresden.inf.st.pnml.distributedPN" version="0.1">
        <node>Executor</node>
        <subnet>SafetyModel</subnet>
        <balloonMarking>
            <tokens>
                <token>{ "color":"NONE","name":"NONE","pickSuccess":"false","placeSuccess":"false",
                    "humanDetected":"false","sensorData":"NONE","trace":"-safety", "locked" : "true" }
                </token>
            </tokens>
        </balloonMarking>
    </toolspecific>
    <initialMarking>
        <text>1</text>
    </initialMarking>
    <name>
        <text>Unsafe</text>
    </name>
</place>

<transition id="SensorServiceCall">
	<toolspecific tool="de.tudresden.inf.st.pnml.distributedPN" version="0.1">
		<type>
			serviceTransitionType
		</type>
		<serviceName>
			sensorService
		</serviceName>
		<serverInput>
			SensorIn
		</serverInput>
		<serverOutput>
			SensorOut
		</serverOutput>
		<serverCapacity>
			1
		</serverCapacity>
		<channels>
			<channel>
				<cid>
					c9
				</cid>
				<request>
					SensorCall
				</request>
				<response>
					SensorResponse
				</response>
			</channel>
		</channels>
	</toolspecific>
	<name>
		<text>
			SensorServiceCall
		</text>
	</name>
</transition>
```



