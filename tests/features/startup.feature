Feature: Start up Gaphor
  Start up gaphor

  Scenario: Launch the application
    Given I load the model "./issue_53.gaphor"
    When I open diagram "Stereotypes diagram"
    Then I have 1 opened diagrams
    
