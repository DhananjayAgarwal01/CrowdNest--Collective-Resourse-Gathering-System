class EmailTemplates:
    @staticmethod
    def request_donation_template(requester_name, donator_name, donation_item, additional_message=None):
        """
        Generate an email template for requesting a donation
        
        :param requester_name: Name of the person requesting the donation
        :param donator_name: Name of the potential donator
        :param donation_item: Item being requested
        :param additional_message: Optional additional context from the requester
        :return: Formatted email body
        """
        template = f"""Dear {donator_name},

I hope this email finds you well. My name is {requester_name}, and I am reaching out regarding the {donation_item} you have listed on CrowdNest.

"""
        if additional_message:
            template += f"Additional Context: {additional_message}\n\n"
        
        template += """I would greatly appreciate your consideration in donating this item. If you are willing to help, please respond to this email, and we can discuss the details of the donation.

Thank you for your kindness and support.

Best regards,
{requester_name}
CrowdNest Community"""
        
        return template
    
    @staticmethod
    def donation_confirmation_template(donator_name, requester_name, donation_item):
        """
        Generate an email template confirming a donation
        
        :param donator_name: Name of the donator
        :param requester_name: Name of the requester
        :param donation_item: Item being donated
        :return: Formatted email body
        """
        return f"""Dear {requester_name},

I am pleased to confirm that I would like to donate the {donation_item} to you through the CrowdNest platform.

Let's discuss the logistics of the donation. Please reply to this email with your preferred method of collection or delivery.

Best regards,
{donator_name}
CrowdNest Community"""
    
    @staticmethod
    def donation_received_template(donator_name, requester_name, donation_item):
        """
        Generate an email template acknowledging receipt of donation
        
        :param donator_name: Name of the donator
        :param requester_name: Name of the requester
        :param donation_item: Item that was donated
        :return: Formatted email body
        """
        return f"""Dear {donator_name},

I wanted to express my heartfelt gratitude for donating the {donation_item}. Your generosity has made a significant difference in my life.

Thank you for being a part of the CrowdNest community and helping those in need.

Warmest regards,
{requester_name}
CrowdNest Community"""
