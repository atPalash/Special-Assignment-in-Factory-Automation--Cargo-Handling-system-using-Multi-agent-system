package contractNet;

import jade.core.Agent;
import jade.core.AID;
import jade.core.behaviours.*;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;
import jade.domain.DFService;
import jade.domain.FIPAException;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;

import java.io.*;
import java.nio.file.*;
import java.util.Objects;

public class initiatorAgent extends Agent {
    // The title of the job
    private String targetJobTitle;
    private String targetjobCoordinates;
    private String userInput;
    // The list of known agents with the specified job capability
    private AID[] responderAgents;

    // Put agent initializations here
    protected void setup() {
        // Printout a welcome message
        System.out.println("Hallo! initiator-agent "+getAID().getName()+" is ready.");

        // Get the title of the job and the 1st goal point to receive cargo and 2nd goal point as a start-up argument
        Object[] args = getArguments();
        if (args != null && args.length > 0) {
            targetjobCoordinates = (String) args[1];
            targetJobTitle = (String) args[0];
            System.out.println("Target job is "+targetJobTitle);
            userInput = targetJobTitle + "," +  targetjobCoordinates;
            System.out.println(userInput);
            // Add a TickerBehaviour that schedules a request to seller agents every minute
            addBehaviour(new TickerBehaviour(this, 60000) {
                protected void onTick() {
                    System.out.println("Trying to allocate "+targetJobTitle);
                    // Update the list of seller agents
                    DFAgentDescription template = new DFAgentDescription();
                    ServiceDescription sd = new ServiceDescription();
                    sd.setType("job");
                    template.addServices(sd);
                    try {
                        DFAgentDescription[] result = DFService.search(myAgent, template);
                        System.out.println("Found the following responder agents:");
                        responderAgents = new AID[result.length];
                        for (int i = 0; i < result.length; ++i) {
                            responderAgents[i] = result[i].getName();
                            System.out.println(responderAgents[i].getName());
                        }
                    }
                    catch (FIPAException fe) {
                        fe.printStackTrace();
                    }

                    // Perform the request
                    myAgent.addBehaviour(new RequestPerformer());
                }
            } );
        }
        else {
            // Make the agent terminate
            System.out.println("No target job title specified");
            doDelete();
        }
    }

    // Put agent clean-up operations here
    protected void takeDown() {
        // Printout a dismissal message
        System.out.println("initiator-agent "+getAID().getName()+" terminating.");
    }

    /**
     Inner class RequestPerformer.
     This is the behaviour used by job-initiator agents to request job-responder
     agents for the target job.
     */

    private class RequestPerformer extends Behaviour {
        private AID bestSeller; // The agent who provides the best offer
        private int bestPrice;  // The best offered price ie. agent with lesser steps to reache 1st goal point
        private int repliesCnt = 0; // The counter of replies from job-responder agents
        private MessageTemplate mt; // The template to receive replies
        private int step = 0;

        public void action() {
            switch (step) {
                case 0:
                    // Send the cfp to all sellers
                    ACLMessage cfp = new ACLMessage(ACLMessage.CFP);
                    for (int i = 0; i < responderAgents.length; ++i) {
                        cfp.addReceiver(responderAgents[i]);
                    }
                    cfp.setContent(userInput);
                    cfp.setConversationId("job");
                    cfp.setReplyWith("cfp"+System.currentTimeMillis()); // Unique value
                    myAgent.send(cfp);
                    // Prepare the template to get proposals
                    mt = MessageTemplate.and(MessageTemplate.MatchConversationId("job"),
                            MessageTemplate.MatchInReplyTo(cfp.getReplyWith()));
                    step = 1;
                    break;
                case 1:
                    // Receive all proposals/refusals from responder agents
                    ACLMessage reply = myAgent.receive(mt);
                    if (reply != null) {
                        // Reply received
                        if (reply.getPerformative() == ACLMessage.PROPOSE) {
                            // This is an offer
                            String posResponder = reply.getContent();
                            //responder agent initial coordinate in 4 X 4 grid of size 20 X 20
                            int x_resp = Character.getNumericValue(posResponder.charAt(0));
                            int y_resp = Character.getNumericValue(posResponder.charAt(1));
                            int[] resCoordinates = {x_resp, y_resp};
                            //initiator agent 1st goal point coordinate for the mobile agents to reach to take cargo
                            int x_ini = Character.getNumericValue(targetjobCoordinates.split(" ")[0].split("-")[1].charAt(0));
                            int y_ini = Character.getNumericValue(targetjobCoordinates.split(" ")[0].split("-")[1].charAt(1));
                            int[] iniCoordinates = {x_ini, y_ini};
                            int steps = new pathPlanner().stepsToGoal(iniCoordinates, resCoordinates);
                            if (bestSeller == null || steps < bestPrice) {
                                // This is the best offer at present
                                bestPrice = steps;
                                bestSeller = reply.getSender();
                            }
                        }
                        repliesCnt++;
                        if (repliesCnt >= responderAgents.length) {
                            // We received all replies
                            step = 2;
                        }
                    }
                    else {
                        block();
                    }
                    break;
                case 2:
                    // Send the purchase order to the responder that provided the best offer ie lesser step to 1st goal point
                    ACLMessage order = new ACLMessage(ACLMessage.ACCEPT_PROPOSAL);
                    order.addReceiver(bestSeller);
                    System.out.println("bestSeller" + bestSeller);
                    order.setContent(targetJobTitle+','+targetjobCoordinates);
                    order.setConversationId("job");
                    order.setReplyWith("order"+System.currentTimeMillis());
                    myAgent.send(order);
                    // Prepare the template to get the purchase order reply
                    mt = MessageTemplate.and(MessageTemplate.MatchConversationId("job"),
                            MessageTemplate.MatchInReplyTo(order.getReplyWith()));
                    step = 3;
                    break;
                case 3:
                    // Receive the purchase order reply
                    reply = myAgent.receive(mt);
                    if (reply != null) {
                        // Purchase order reply received
                        if (reply.getPerformative() == ACLMessage.INFORM) {
                            // Purchase successful. We can terminate
                            System.out.println(targetJobTitle+" successfully purchased from agent "+reply.getSender().getName());
                            System.out.println("Price = "+bestPrice);
                            String instruction;
                            System.out.println(reply);
                            try {
                                String fs = System.getProperty("file.separator");
                                // .txt file to store the communication between initiator and responder agents. the
                                // python file static_robotServer watches for this file change and starts the robot
                                // behavior accordingly
                                String path_javaReply = fs + "home" + fs + "pi" + fs + "Desktop" + fs + "testingFiles" + fs + "19.08.17" + fs + "java_reply.txt";
                                FileWriter writer = new FileWriter(path_javaReply, false);
                                instruction = reply.getContent();
                                BufferedWriter bufferedWriter = new BufferedWriter(writer);
                                bufferedWriter.write(instruction);
                                bufferedWriter.close();
                                WatchService watcher = FileSystems.getDefault().newWatchService();
                                Path dir = Paths.get(fs + "home" + fs + "pi" + fs + "Desktop" + fs + "testingFiles" + fs + "19.08.17");
                                dir.register(watcher, StandardWatchEventKinds.ENTRY_MODIFY);
                                int count = 0;
                                while (true){
                                    count++;
                                    System.out.println(count);
                                    WatchKey key;
                                    try {
                                        key = watcher.take();
                                    } catch (InterruptedException ex) {
                                        return;
                                    }
                                    for (WatchEvent<?> event : key.pollEvents()) {
                                        WatchEvent.Kind<?> kind = event.kind();
                                        @SuppressWarnings("unchecked")
                                        WatchEvent<Path> ev = (WatchEvent<Path>) event;
                                        Path fileName = ev.context();
                                        System.out.println(fileName);
                                        // initiator watching the .txt file to know when the unloading is complete so that it can delete the initiator agent
                                        if (kind == StandardWatchEventKinds.OVERFLOW) {
                                            System.out.println("overflow error");
                                        }
                                        else if (kind == StandardWatchEventKinds.ENTRY_MODIFY && Objects.equals(fileName.toString(), "python_reply.txt")) {
                                            System.out.println("File modified" + fileName);
                                            String path_r = fs + "home" + fs + "pi" + fs + "Desktop" + fs + "testingFiles" + fs + "19.08.17" + fs +  "python_reply.txt";
                                            BufferedReader fr = new BufferedReader(new FileReader(path_r));
                                            String line = fr.readLine();
                                            System.out.println(line);
                                            if(Objects.equals(line, "loaded")){
                                                System.out.println("in delete");
                                                myAgent.doDelete();
                                            }
                                        }
                                    }
                                    boolean valid = key.reset();
                                    if (!valid) {
                                        break;
                                    }
                                }
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                        }
                        else {
                            System.out.println("Attempt failed: requested job already sold.");
                        }

                        step = 4;
                    }
                    else {
                        block();
                    }
                    break;
            }
        }

        public boolean done() {
            if (step == 2 && bestSeller == null) {
                System.out.println("Attempt failed: "+targetJobTitle+" not available for sale");
            }
            return ((step == 2 && bestSeller == null) || step == 4);
        }
    }  // End of inner class RequestPerformer
}
